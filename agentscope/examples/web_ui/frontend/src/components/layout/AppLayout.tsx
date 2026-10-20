import { useQuery } from '@tanstack/react-query';
import { Outlet } from 'react-router-dom';

import { healthApi } from '@/api';
import { getBaseUrl, getUserId } from '@/api/client';
import { AppSidebar } from '@/components/layout/AppSidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';

export function AppLayout() {
	const { data: health } = useQuery({
		queryKey: ['control-health', getBaseUrl(), getUserId()],
		queryFn: () => healthApi.check(getBaseUrl() || window.location.origin, getUserId()),
		staleTime: 60_000,
		retry: false,
	});
	return (
		<div className="h-screen flex">
			<SidebarProvider>
				<AppSidebar />
				<SidebarInset className="flex-1 overflow-hidden bg-canvas">
					<header className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-1 px-4 pb-1 pt-3">
						<span className="text-sm font-semibold">Agent 总控台</span>
						<span className="text-xs text-muted-foreground">AgentScope {health?.version || '2'} · 官方 Web UI</span>
						<span className="ml-auto text-xs text-muted-foreground">配置模型后可运行 Agent 任务</span>
					</header>
					<div className="min-h-0 flex-1 overflow-hidden"><Outlet /></div>
				</SidebarInset>
			</SidebarProvider>
		</div>
	);
}
