/* Real browser deployment verification; never creates credentials or calls a model. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const zlib = require('node:zlib');

// A small technical PNG fixture, generated without external assets.
function fixturePng() {
  const crc32 = buffer => {
    let crc = 0xffffffff;
    for (const byte of buffer) {
      crc ^= byte;
      for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
    }
    return (crc ^ 0xffffffff) >>> 0;
  };
  const chunk = (name, bytes) => {
    const type = Buffer.from(name);
    const size = Buffer.alloc(4);
    size.writeUInt32BE(bytes.length);
    const checksum = Buffer.alloc(4);
    checksum.writeUInt32BE(crc32(Buffer.concat([type, bytes])));
    return Buffer.concat([size, type, bytes, checksum]);
  };
  const width = 160;
  const height = 80;
  const pixels = Buffer.alloc((width * 3 + 1) * height);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const offset = y * (width * 3 + 1) + x * 3 + 1;
      pixels[offset] = 30 + Math.floor(x / 2);
      pixels[offset + 1] = 110 + y;
      pixels[offset + 2] = 170;
    }
  }
  const header = Buffer.alloc(13);
  header.writeUInt32BE(width, 0);
  header.writeUInt32BE(height, 4);
  header[8] = 8;
  header[9] = 2;
  return Buffer.concat([Buffer.from('89504e470d0a1a0a', 'hex'), chunk('IHDR', header), chunk('IDAT', zlib.deflateSync(pixels)), chunk('IEND', Buffer.alloc(0))]);
}

async function main() {
  const evidence = path.resolve(__dirname, '../runtime/evidence');
  await fs.mkdir(evidence, { recursive: true });
  const fixturePath = path.join(evidence, 'vault-technical-fixture.png');
  await fs.writeFile(fixturePath, fixturePng());
  const origin = 'http://127.0.0.1:8765';
  const notePath = '90_归档/总控台部署验收.md';
  const verification = {
    started_at: new Date().toISOString(),
    origin,
    scope: '真实浏览器部署验收；不证明模型推理、跨Agent执行或外部平台接通',
    model_calls: 0,
    credentials_written: 0,
    checks: [],
    errors: [],
    failed_requests: [],
    unexpected_mutations: [],
  };
  const check = (name, detail) => verification.checks.push({ name, status: 'PASS', detail });
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  let page;
  try {
    page = await browser.newPage({ viewport: { width: 1500, height: 980 }, locale: 'zh-CN' });
    page.setDefaultTimeout(15_000);
    page.on('pageerror', error => verification.errors.push(error.message));
    page.on('requestfailed', request => verification.failed_requests.push({ url: request.url(), error: request.failure()?.errorText }));
    page.on('request', request => {
      const pathname = new URL(request.url()).pathname;
      if (!['GET', 'HEAD', 'OPTIONS'].includes(request.method()) && !pathname.startsWith('/control/vault/')) {
        verification.unexpected_mutations.push({ method: request.method(), path: pathname });
      }
    });
    await page.goto(origin, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#server-url-input').inputValue(), origin);
    assert.equal(await page.locator('#username-input').inputValue(), 'local');
    await page.screenshot({ path: path.join(evidence, 'console-first-open.png'), fullPage: true });
    check('首次连接默认值', { service: origin, user: 'local' });

    await page.getByRole('button', { name: '开始使用', exact: true }).click();
    await page.waitForURL(/\/chat/);
    await page.getByRole('button', { name: '跳过', exact: true }).waitFor({ state: 'visible', timeout: 5000 }).then(() => page.getByRole('button', { name: '跳过', exact: true }).click()).catch(() => {});
    await page.getByText('Agent 总控台', { exact: true }).waitFor();
    check('首次连接提交', { url: page.url(), title: await page.title() });

    const agentsResponse = await page.request.get(`${origin}/agent/`);
    assert.equal(agentsResponse.status(), 200);
    const agents = await agentsResponse.json();
    assert.equal(agents.agents.length, 2);
    assert.deepEqual(agents.agents.map(agent => agent.data.name).sort(), ['总控 Agent', '知识整理 Agent'].sort());
    const agentPicker = page.getByRole('button', { name: /^(总控 Agent|知识整理 Agent)$/ }).first();
    await agentPicker.click();
    await page.getByRole('menuitem', { name: '总控 Agent', exact: true }).waitFor();
    await page.getByRole('menuitem', { name: '知识整理 Agent', exact: true }).waitFor();
    await page.screenshot({ path: path.join(evidence, 'console-agents.png'), fullPage: true });
    await page.keyboard.press('Escape');
    check('两个默认 Agent 在真实页面可见', { count: agents.agents.length, names: agents.agents.map(agent => agent.data.name) });

    await page.getByRole('button', { name: 'Obsidian 知识仓', exact: true }).click();
    await page.waitForURL(`${origin}/vault`);
    await page.getByRole('heading', { name: '知识仓', exact: true }).waitFor();
    const statusResponse = await page.request.get(`${origin}/control/vault/status`);
    assert.equal(statusResponse.status(), 200);
    const status = await statusResponse.json();
    assert.equal(status.exists, true);
    check('知识仓列表读取', { note_count: status.note_count, attachment_count: status.attachment_count });

    const existing = await page.request.get(`${origin}/control/vault/note?path=${encodeURIComponent(notePath)}`);
    const existed = existing.status() === 200;
    if (existed) {
      await page.getByRole('textbox', { name: '搜索知识仓' }).fill('总控台部署验收');
      await page.getByRole('button', { name: /总控台部署验收/ }).click();
    } else {
      assert.equal(existing.status(), 404);
      await page.getByRole('button', { name: '新建笔记', exact: true }).click();
      assert.match(await page.getByRole('textbox', { name: '笔记相对路径' }).inputValue(), /^00_收件箱\//);
      await page.getByRole('textbox', { name: '笔记相对路径' }).fill(notePath);
    }
    const noteContent = '---\ntitle: 总控台部署验收\nproject: Agent智能操作系统\nstatus: deployment-verified\ntags: [部署验收, 浏览器]\n---\n\n# 总控台部署验收\n\n这是浏览器部署验收记录，不是模型推理结果。\n\n已通过实际页面验证首次连接、两个默认 Agent 可见、知识仓搜索、笔记新建编辑保存与图片上传预览。\n\n本轮没有写入模型凭据、没有发送模型请求，也不证明外部 AI 平台已连接。\n\n检索标记：browser-deployment-check-2026-10-21\n';
    await page.getByRole('textbox', { name: 'Markdown 正文' }).fill(noteContent);
    const firstSaveResponse = page.waitForResponse(response => response.request().method() === 'PUT' && new URL(response.url()).pathname === '/control/vault/note');
    await page.getByRole('button', { name: '保存笔记', exact: true }).click();
    const firstSave = await firstSaveResponse;
    assert.equal(firstSave.status(), 200);
    const firstSaved = await firstSave.json();
    assert.match(firstSaved.sha256, /^[a-f\d]{64}$/);
    await page.getByText('已保存到 Obsidian 知识仓。', { exact: true }).waitFor();
    check(existed ? '已有验收笔记编辑保存（幂等重跑）' : '浏览器新建笔记并保存', { path: notePath, created: firstSaved.created, sha256: firstSaved.sha256 });

    const uploadResponse = page.waitForResponse(response => response.request().method() === 'POST' && new URL(response.url()).pathname === '/control/vault/attachments');
    await page.getByLabel('选择上传图片', { exact: true }).setInputFiles(fixturePath);
    const upload = await uploadResponse;
    assert.equal(upload.status(), 201);
    const attachment = await upload.json();
    await page.getByText('图片已上传，引用已插入正文。保存笔记后会写入文件。', { exact: true }).waitFor();
    assert.ok((await page.getByRole('textbox', { name: 'Markdown 正文' }).inputValue()).includes(attachment.markdown));
    const finalSaveResponse = page.waitForResponse(response => response.request().method() === 'PUT' && new URL(response.url()).pathname === '/control/vault/note');
    await page.getByRole('button', { name: '保存笔记', exact: true }).click();
    const finalSave = await finalSaveResponse;
    assert.equal(finalSave.status(), 200);
    assert.equal(finalSave.request().postDataJSON().expected_sha256, firstSaved.sha256);
    const finalSaved = await finalSave.json();
    await page.getByText('已保存到 Obsidian 知识仓。', { exact: true }).waitFor();
    check('图片真实上传并携带旧版本保存', { attachment: attachment.path, upload_http_status: upload.status(), sha256: finalSaved.sha256 });

    await page.getByRole('button', { name: '正文与图片预览', exact: true }).click();
    const image = page.locator(`img[src*="/control/vault/attachment"]`).first();
    await image.waitFor();
    await image.evaluate(element => new Promise((resolve, reject) => {
      if (element.complete) return element.naturalWidth > 0 ? resolve(true) : reject(new Error('Image failed to decode'));
      element.addEventListener('load', () => resolve(true), { once: true });
      element.addEventListener('error', () => reject(new Error('Image failed to decode')), { once: true });
    }));
    const imageInfo = await image.evaluate(element => ({ src: element.src, naturalWidth: element.naturalWidth, naturalHeight: element.naturalHeight }));
    assert.equal(imageInfo.naturalWidth, 160);
    assert.equal(imageInfo.naturalHeight, 80);
    const attachmentResponse = await page.request.get(new URL(attachment.url, origin).toString());
    assert.equal(attachmentResponse.status(), 200);
    const attachmentFile = path.join(status.root, attachment.path);
    const noteFile = path.join(status.root, notePath);
    assert.ok((await fs.stat(attachmentFile)).size > 0);
    assert.ok((await fs.readFile(noteFile, 'utf8')).includes(attachment.markdown));
    check('图片预览、下载响应及实际文件', { ...imageInfo, http_status: attachmentResponse.status(), file: attachmentFile });

    const searchResponse = page.waitForResponse(response => new URL(response.url()).pathname === '/control/vault/notes' && new URL(response.url()).searchParams.get('query') === 'browser-deployment-check-2026-10-21');
    await page.getByRole('textbox', { name: '搜索知识仓' }).fill('browser-deployment-check-2026-10-21');
    const search = await searchResponse;
    assert.equal(search.status(), 200);
    const found = await search.json();
    assert.ok(found.items.some(item => item.path === notePath));
    await page.getByRole('button', { name: /总控台部署验收/ }).waitFor();
    await page.screenshot({ path: path.join(evidence, 'console-vault.png'), fullPage: true });
    check('真实关键词搜索命中', { query: 'browser-deployment-check-2026-10-21', total: found.total, matched_path: notePath });

    const consoleStatus = await (await page.request.get(`${origin}/control/status`)).json();
    assert.equal(consoleStatus.model_runtime, 'not-configured');
    assert.equal(consoleStatus.credential_count, 0);
    assert.equal(verification.unexpected_mutations.length, 0);
    assert.equal(verification.errors.length, 0);
    check('模型与凭据边界', { model_runtime: consoleStatus.model_runtime, credential_count: consoleStatus.credential_count, unexpected_mutations: verification.unexpected_mutations });
    verification.status = 'PASS';
    verification.title = await page.title();
    verification.note_path = noteFile;
    verification.attachment_path = attachmentFile;
    verification.screenshots = ['console-first-open.png', 'console-agents.png', 'console-vault.png'];
  } catch (error) {
    verification.status = 'FAIL';
    verification.failure = { message: error.message, stack: error.stack };
    if (page) {
      verification.page_text_on_failure = (await page.locator('body').innerText().catch(() => '')).slice(0, 12_000);
      await page.screenshot({ path: path.join(evidence, 'console-failure.png'), fullPage: true }).catch(() => {});
    }
    throw error;
  } finally {
    verification.finished_at = new Date().toISOString();
    await fs.writeFile(path.join(evidence, 'browser-verification.json'), JSON.stringify(verification, null, 2), 'utf8');
    console.log(JSON.stringify(verification, null, 2));
    await browser.close();
  }
}

async function verifyLayout() {
  const evidence = path.resolve(__dirname, '../runtime/evidence');
  await fs.mkdir(evidence, { recursive: true });
  const report = { started_at: new Date().toISOString(), checks: [], errors: [], model_calls: 0, credentials_written: 0 };
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 980 }, locale: 'zh-CN' });
    page.on('pageerror', error => report.errors.push(error.message));
    await page.goto('http://127.0.0.1:8765', { waitUntil: 'networkidle' });
    const hint = '本地前后端已在同一端口运行，用户名沿用 local。当前为单用户部署，不提供登录隔离。';
    await page.getByText(hint, { exact: true }).waitFor();
    await page.screenshot({ path: path.join(evidence, 'console-setup-final.png'), fullPage: true });
    report.checks.push({ name: '本地单用户连接提示', status: 'PASS', text: hint });
    await page.getByRole('button', { name: '开始使用', exact: true }).click();
    await page.waitForURL(/\/chat/);
    await page.getByRole('button', { name: '跳过', exact: true }).waitFor({ state: 'visible', timeout: 5000 }).then(() => page.getByRole('button', { name: '跳过', exact: true }).click()).catch(() => {});
    const chatLayout = await page.locator('main.flex.size-full').boundingBox();
    assert.ok(chatLayout && chatLayout.height > 850, `Chat area too short: ${chatLayout?.height}`);
    await page.getByRole('button', { name: /^(总控 Agent|知识整理 Agent)$/ }).first().click();
    await page.getByRole('menuitem', { name: '总控 Agent', exact: true }).waitFor();
    await page.getByRole('menuitem', { name: '知识整理 Agent', exact: true }).waitFor();
    await page.screenshot({ path: path.join(evidence, 'console-agents-final.png'), fullPage: true });
    report.checks.push({ name: '聊天区铺满可用高度', status: 'PASS', viewport: { width: 1500, height: 980 }, chat_bounds: chatLayout });
    await page.keyboard.press('Escape');
    await page.getByRole('button', { name: 'Obsidian 知识仓', exact: true }).click();
    await page.getByRole('button', { name: '新建笔记', exact: true }).click();
    const defaultPath = await page.getByRole('textbox', { name: '笔记相对路径' }).inputValue();
    assert.match(defaultPath, /^00_收件箱\//);
    const localDate = await page.evaluate(() => {
      const now = new Date();
      return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    });
    assert.ok(defaultPath.includes(localDate), 'The default note name must use the local calendar date.');
    await page.screenshot({ path: path.join(evidence, 'console-vault-new-note.png'), fullPage: true });
    report.checks.push({ name: '新建笔记默认目录及本地日期', status: 'PASS', default_path: defaultPath, local_date: localDate, saved: false });
    assert.equal(report.errors.length, 0);
    report.status = 'PASS';
  } catch (error) {
    report.status = 'FAIL';
    report.failure = error.message;
    throw error;
  } finally {
    report.finished_at = new Date().toISOString();
    await fs.writeFile(path.join(evidence, 'console-layout-verification.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report, null, 2));
    await browser.close();
  }
}

(process.argv.includes('--layout-only') ? verifyLayout() : main()).catch(error => { console.error(error); process.exitCode = 1; });
