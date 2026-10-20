import { AlertCircle, FileText, ImagePlus, Loader2, Plus, RefreshCw, Save, Search } from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useBlocker } from 'react-router-dom';

import { ApiError } from '@/api/client';
import { vaultApi } from '@/api/vault';
import type { VaultNote, VaultNoteSummary, VaultStatus } from '@/api/vault';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

function describeError(error: unknown): string {
	return error instanceof Error ? error.message : '请求失败，请检查知识仓服务。';
}

/** Preview only vault-local images. Note text is never evaluated as HTML. */
function findImages(content: string, notePath: string) {
	const result: { path: string; label: string }[] = [];
	const matches = content.matchAll(/!\[([^\]]*)\]\(([^)\n]+)\)|!\[\[([^\]\n]+)\]\]/g);
	for (const match of matches) {
		const raw = (match[2] || match[3] || '').trim();
		let path = raw.split('|')[0];
		try {
			if (path.startsWith('/control/vault/attachment?')) {
				path = new URL(path, window.location.origin).searchParams.get('path') || '';
			} else {
				path = decodeURIComponent(path);
				if (path.startsWith('./') || path.startsWith('../')) {
					const folder = notePath.split('/').slice(0, -1).join('/');
					path = new URL(path, `https://vault.local/${folder}/`).pathname.slice(1);
				}
			}
		} catch {
			continue;
		}
		if (!path || /^(?:[a-z][a-z\d+.-]*:|\/\/|\/)/i.test(path) || path.split('/').includes('..')) continue;
		if (!/\.(png|jpe?g|webp|gif)$/i.test(path)) continue;
		if (!result.some((image) => image.path === path)) result.push({ path, label: match[1] || path.split('/').pop() || '图片' });
	}
	return result;
}

export function VaultPage() {
	const [status, setStatus] = useState<VaultStatus | null>(null);
	const [notes, setNotes] = useState<VaultNoteSummary[]>([]);
	const [total, setTotal] = useState(0);
	const [query, setQuery] = useState('');
	const [folder, setFolder] = useState('');
	const [listLoading, setListLoading] = useState(true);
	const [listError, setListError] = useState('');
	const [note, setNote] = useState<VaultNote | null>(null);
	const [path, setPath] = useState('');
	const [content, setContent] = useState('');
	const [isNew, setIsNew] = useState(false);
	const [loadingNote, setLoadingNote] = useState(false);
	const [saving, setSaving] = useState(false);
	const [uploading, setUploading] = useState(false);
	const [editorError, setEditorError] = useState('');
	const [conflict, setConflict] = useState(false);
	const [message, setMessage] = useState('');
	const [preview, setPreview] = useState(false);
	const fileInput = useRef<HTMLInputElement>(null);
	const editor = useRef<HTMLTextAreaElement>(null);
	const listRequest = useRef(0);
	const noteRequest = useRef(0);
	const active = isNew || note !== null;
	const dirty = isNew || (note !== null && content !== note.content);
	const busy = saving || uploading || loadingNote;
	const images = useMemo(() => findImages(content, path), [content, path]);
	const blocker = useBlocker(dirty || saving || uploading);

	useEffect(() => {
		if (blocker.state !== 'blocked') return;
		if (saving || uploading) {
			blocker.reset();
			setMessage('正在保存或上传，请稍候完成再离开。');
		} else if (window.confirm('当前笔记有未保存的修改。放弃修改并离开知识仓？')) {
			blocker.proceed();
		} else blocker.reset();
	}, [blocker, saving, uploading]);

	const refresh = useCallback(async () => {
		const request = ++listRequest.current;
		setListLoading(true);
		setListError('');
		try {
			const [nextStatus, list] = await Promise.all([vaultApi.status(), vaultApi.list(query, folder)]);
			if (request !== listRequest.current) return;
			setStatus(nextStatus);
			setNotes(list.items);
			setTotal(list.total);
		} catch (error) {
			if (request === listRequest.current) setListError(describeError(error));
		} finally {
			if (request === listRequest.current) setListLoading(false);
		}
	}, [query, folder]);

	useEffect(() => {
		const timeout = window.setTimeout(() => void refresh(), 250);
		return () => window.clearTimeout(timeout);
	}, [refresh]);

	useEffect(() => {
		if (!dirty) return;
		const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); };
		window.addEventListener('beforeunload', warn);
		return () => window.removeEventListener('beforeunload', warn);
	}, [dirty]);

	const canLeave = () => !dirty || window.confirm('当前笔记有未保存的修改。放弃修改并继续？');

	const openNote = async (nextPath: string, discard = false) => {
		if (busy || (!discard && !canLeave())) return;
		const request = ++noteRequest.current;
		setLoadingNote(true);
		setEditorError('');
		setMessage('');
		try {
			const loaded = await vaultApi.read(nextPath);
			if (request !== noteRequest.current) return;
			setNote(loaded);
			setPath(loaded.path);
			setContent(loaded.content);
			setIsNew(false);
			setConflict(false);
		} catch (error) {
			if (request === noteRequest.current) setEditorError(describeError(error));
		} finally {
			if (request === noteRequest.current) setLoadingNote(false);
		}
	};

	const newNote = () => {
		if (busy || !canLeave()) return;
		++noteRequest.current;
		const now = new Date();
		const pad = (value: number) => String(value).padStart(2, '0');
		const stamp = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}-${pad(now.getHours())}-${pad(now.getMinutes())}-${pad(now.getSeconds())}-${String(now.getMilliseconds()).padStart(3, '0')}`;
		setNote(null);
		setPath(`00_收件箱/笔记-${stamp}.md`);
		setContent('# 新笔记\n\n');
		setIsNew(true);
		setConflict(false);
		setEditorError('');
		setMessage('');
		setPreview(false);
	};

	const save = async () => {
		if (!active || busy || conflict) return;
		const target = path.trim().replace(/\\/g, '/');
		if (!target.endsWith('.md') || target.startsWith('/') || target.split('/').includes('..')) {
			setEditorError('请填写知识仓内的相对路径，并以 .md 结尾，例如 00_收件箱/新笔记.md。');
			return;
		}
		if (!isNew && !note?.sha256) {
			setEditorError('缺少原文件版本，无法安全保存。请重新载入笔记。');
			return;
		}
		setSaving(true);
		setEditorError('');
		setMessage('');
		try {
			const saved = await vaultApi.save(target, content, isNew ? undefined : note!.sha256);
			setNote(saved);
			setPath(saved.path);
			setContent(saved.content);
			setIsNew(false);
			setConflict(false);
			setMessage('已保存到 Obsidian 知识仓。');
			void refresh();
		} catch (error) {
			if (error instanceof ApiError && error.status === 409) {
				setConflict(true);
				setEditorError('文件已在 Obsidian 或其他窗口中更新，或新建路径已存在。你的编辑仍保留在下方。请先复制内容，再重新载入最新版本进行合并；新笔记可改用其他路径。');
			} else setEditorError(describeError(error));
		} finally {
			setSaving(false);
		}
	};

	const upload = async (file: File) => {
		if (!active || busy) return;
		if (!/^image\/(png|jpeg|webp|gif)$/.test(file.type)) {
			setEditorError('请选择 PNG、JPEG、WebP 或 GIF 图片。');
			return;
		}
		const start = editor.current?.selectionStart ?? content.length;
		const end = editor.current?.selectionEnd ?? start;
		setUploading(true);
		setEditorError('');
		setMessage('');
		try {
			const attachment = await vaultApi.upload(file);
			const inserted = `\n${attachment.markdown}\n`;
			setContent((value) => value.slice(0, start) + inserted + value.slice(end));
			setMessage('图片已上传，引用已插入正文。保存笔记后会写入文件。');
			setPreview(false);
			void refresh();
		} catch (error) {
			setEditorError(describeError(error));
		} finally {
			setUploading(false);
			if (fileInput.current) fileInput.current.value = '';
		}
	};

	return (
		<div className="flex size-full min-h-0 flex-col gap-2 p-2 lg:flex-row">
			<aside className="flex max-h-[45%] min-h-48 shrink-0 flex-col rounded-[22px] bg-sidebar lg:h-full lg:max-h-none lg:w-80">
				<div className="space-y-3 p-5">
					<div className="flex items-start justify-between gap-2">
						<div><h1 className="text-xl font-medium tracking-tight">知识仓</h1><p className="mt-1 text-xs text-muted-foreground">Obsidian · 本地 Markdown 与图片</p></div>
						<Button variant="ghost" size="icon-sm" title="刷新知识仓" aria-label="刷新知识仓" onClick={() => void refresh()} disabled={listLoading}><RefreshCw className={cn('size-4', listLoading && 'animate-spin')} /></Button>
					</div>
					{status && <p className="text-xs text-muted-foreground" title={status.root}>{status.name} · {status.note_count} 篇笔记 · {status.attachment_count} 个附件</p>}
					<label className="relative block"><Search className="absolute left-3 top-2.5 size-4 text-muted-foreground" /><Input className="pl-9" placeholder="搜索标题、正文、标签…" aria-label="搜索知识仓" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
					<Input placeholder="按文件夹筛选（可选）" aria-label="按文件夹筛选" value={folder} onChange={(event) => setFolder(event.target.value)} />
					<Button className="w-full" variant="outline" onClick={newNote} disabled={busy || !status?.exists}><Plus className="size-4" />新建笔记</Button>
				</div>
				<div className="min-h-0 flex-1 overflow-y-auto px-2 pb-3" aria-busy={listLoading}>
					{listError ? <Alert variant="destructive"><AlertCircle /><AlertDescription>{listError}<Button variant="outline" size="sm" className="mt-2" onClick={() => void refresh()}>重试</Button></AlertDescription></Alert> : status && !status.exists ? <p className="px-3 text-sm text-destructive">知识仓目录不存在，请检查服务端设置。</p> : listLoading && notes.length === 0 ? <p className="p-3 text-sm text-muted-foreground">正在读取知识仓…</p> : notes.length === 0 ? <p className="p-3 text-sm text-muted-foreground">{query || folder ? '没有找到匹配的笔记。' : '知识仓里还没有笔记，点击“新建笔记”开始。'}</p> : notes.map((item) => (
						<button key={item.path} className={cn('mb-1 w-full rounded-xl px-3 py-3 text-left transition-colors hover:bg-sidebar-accent disabled:opacity-60', !isNew && path === item.path && 'bg-sidebar-accent')} onClick={() => void openNote(item.path)} disabled={busy}>
							<div className="flex items-center gap-2"><FileText className="size-4 shrink-0 text-muted-foreground" /><span className="truncate text-sm font-medium">{item.title || item.path}</span></div>
							<p className="mt-1 truncate text-xs text-muted-foreground" title={item.path}>{item.path}</p>
							{(item.project || item.status || item.tags?.length > 0) && <div className="mt-2 flex flex-wrap gap-1">{item.project && <Badge variant="outline">{item.project}</Badge>}{item.status && <Badge variant="secondary">{item.status}</Badge>}{item.tags?.slice(0, 3).map((tag) => <span className="text-xs text-muted-foreground" key={tag}>#{tag}</span>)}</div>}
						</button>
					))}
				</div>
				<p className="px-5 pb-4 text-xs text-muted-foreground">{listLoading ? '更新中…' : `${total} 篇匹配笔记`} · 文件修改可同步在 Obsidian 中查看</p>
			</aside>
			<section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-[22px] bg-card shadow-panel">
				{loadingNote && <p className="flex items-center gap-2 border-b p-4 text-sm" role="status"><Loader2 className="size-4 animate-spin" />正在读取笔记…</p>}
				{editorError && <Alert variant="destructive" className="m-4 w-auto"><AlertCircle /><AlertDescription>{editorError}{conflict && !isNew && <Button className="mt-2 w-fit" variant="outline" size="sm" onClick={() => { if (window.confirm('请先复制需保留的编辑。重新载入将放弃当前修改，继续？')) void openNote(path, true); }} disabled={busy}>重新载入最新版本</Button>}</AlertDescription></Alert>}
				{!active ? <div className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-center text-muted-foreground"><FileText className="size-10" /><h2 className="text-lg font-medium text-foreground">选择或新建一篇笔记</h2><p className="max-w-md text-sm">在这里管理项目知识、操作经验和图片。笔记直接保存在本地知识仓，原生 AgentScope 检索库仍由侧栏的“知识库”管理。</p></div> : <>
					<div className="space-y-3 border-b p-4">
						<div className="flex flex-wrap items-center gap-2">
							<h2 className="mr-auto text-base font-medium">{isNew ? '新建笔记' : (notes.find((item) => item.path === path)?.title || path.split('/').pop())}</h2>
							{dirty && <Badge variant="outline">未保存</Badge>}
							<Button variant="outline" size="sm" onClick={() => setPreview(!preview)}>{preview ? '返回编辑' : '正文与图片预览'}</Button>
							<Button variant="outline" size="sm" disabled={busy} onClick={() => fileInput.current?.click()}>{uploading ? <Loader2 className="size-4 animate-spin" /> : <ImagePlus className="size-4" />}上传图片</Button>
							<Button size="sm" onClick={() => void save()} disabled={busy || !dirty || conflict}>{saving ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />}{saving ? '保存中…' : '保存笔记'}</Button>
						</div>
						<label className="flex items-center gap-2 text-xs text-muted-foreground"><span className="shrink-0">文件路径</span><Input className="h-8 font-mono text-xs" value={path} readOnly={!isNew} onChange={(event) => { setPath(event.target.value); if (isNew) setConflict(false); }} disabled={busy} aria-label="笔记相对路径" /></label>
						<p className="text-xs text-muted-foreground">Markdown 原文编辑；图片存为知识仓附件。其他应用修改同一文件时，会先提示合并冲突。</p>
						<input ref={fileInput} type="file" accept="image/png,image/jpeg,image/webp,image/gif" className="hidden" aria-label="选择上传图片" onChange={(event) => { const file = event.target.files?.[0]; if (file) void upload(file); }} />
					</div>
					{message && <p className="px-4 pt-3 text-sm text-muted-foreground" role="status">{message}</p>}
					{preview ? <div className="flex-1 space-y-6 overflow-y-auto p-5"><pre className="whitespace-pre-wrap break-words font-mono text-sm">{content}</pre>{images.length > 0 && <div className="space-y-3 border-t pt-4"><h3 className="text-sm font-medium">本地附件预览</h3>{images.map((image) => <figure key={image.path} className="rounded-lg border p-3"><img src={vaultApi.attachmentUrl(image.path)} alt={image.label} className="max-h-96 max-w-full rounded object-contain" loading="lazy" /><figcaption className="mt-2 break-all text-xs text-muted-foreground">{image.path}</figcaption></figure>)}</div>}</div> : <Textarea ref={editor} className="min-h-64 flex-1 resize-none rounded-none border-0 bg-transparent p-5 font-mono text-sm leading-7 shadow-none focus-visible:ring-0 lg:min-h-0" value={content} onChange={(event) => { setContent(event.target.value); setMessage(''); }} readOnly={busy} spellCheck={false} aria-label="Markdown 正文" />}
				</>}
			</section>
		</div>
	);
}
