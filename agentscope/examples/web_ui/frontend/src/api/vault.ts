import { ApiError, client, getBaseUrl, getUserId } from './client';

export interface VaultStatus {
	name: string;
	root: string;
	exists: boolean;
	note_count: number;
	attachment_count: number;
}

export interface VaultNoteSummary {
	path: string;
	title: string;
	project?: string;
	status?: string;
	tags: string[];
	updated_at: string;
	size: number;
}

export interface VaultNote {
	path: string;
	content: string;
	sha256: string;
	metadata: Record<string, unknown>;
}

export interface VaultAttachment {
	path: string;
	name: string;
	url: string;
	markdown: string;
}

const baseUrl = () => getBaseUrl() || window.location.origin;
const options = () => ({ silent: true, baseUrl: baseUrl(), timeoutMs: 20_000 });

export const vaultApi = {
	status: () => client.get<VaultStatus>('/control/vault/status', undefined, options()),
	list: (query = '', folder = '') =>
		client.get<{ items: VaultNoteSummary[]; total: number }>(
			'/control/vault/notes',
			{ query, folder },
			options(),
		),
	read: (path: string) => client.get<VaultNote>('/control/vault/note', { path }, options()),
	save: async (path: string, content: string, expectedSha256?: string): Promise<VaultNote> => {
		const response = await client.stream('/control/vault/note', {
			method: 'PUT',
			body: { path, content, ...(expectedSha256 ? { expected_sha256: expectedSha256 } : {}) },
			...options(),
		});
		return response.json() as Promise<VaultNote>;
	},
	upload: async (file: File): Promise<VaultAttachment> => {
		const body = new FormData();
		body.append('file', file);
		let response: Response;
		try {
			response = await fetch(new URL('/control/vault/attachments', baseUrl()), {
				method: 'POST',
				headers: { 'X-User-ID': getUserId() },
				body,
				signal: AbortSignal.timeout(60_000),
			});
		} catch (error) {
			throw new ApiError(
				0,
				error instanceof DOMException && error.name === 'TimeoutError'
					? '图片上传超时，请检查服务后重试。'
					: '无法连接知识仓服务，请检查服务器地址。',
			);
		}
		if (!response.ok) {
			const body = await response.text();
			let detail = body || response.statusText;
			try {
				const payload = JSON.parse(body) as { detail?: unknown };
				if (payload.detail) detail = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail);
			} catch {
				// Keep the actual non-JSON response for the inline error.
			}
			throw new ApiError(response.status, detail);
		}
		return response.json() as Promise<VaultAttachment>;
	},
	attachmentUrl: (path: string) => {
		const url = new URL('/control/vault/attachment', baseUrl());
		url.searchParams.set('path', path);
		return url.toString();
	},
};
