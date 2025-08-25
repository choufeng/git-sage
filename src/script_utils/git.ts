import { execa } from 'execa';
import { logger } from '../utils/logger';

export async function getGitDiff(): Promise<string | null> {
    try {
        const mainBranch = await getMainBranchName();
        const { stdout } = await execa('git', ['diff', `${mainBranch}...HEAD`]);
        return stdout || null;
    } catch (error) {
        logger.error('获取代码差异时发生错误：', error);
        return null;
    }
}

export async function getMainBranchName(): Promise<string> {
    try {
        // 尝试获取默认分支名称
        const { stdout: remoteHead } = await execa('git', ['symbolic-ref', 'refs/remotes/origin/HEAD']);
        return remoteHead.split('/').pop() || 'main';
    } catch {
        // 如果获取失败，返回默认值 'main'
        return 'main';
    }
}

export async function isGitRepository(): Promise<boolean> {
    try {
        await execa('git', ['rev-parse', '--is-inside-work-tree']);
        return true;
    } catch {
        return false;
    }
}