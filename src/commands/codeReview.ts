import { getGitDiff } from '../utils/git';
import { getChatResponse } from '../utils/ai';
import { loadPrompt } from '../utils/prompt';
import { logger } from '../utils/logger';
import { isGitRepository } from '../utils/git';

export async function handleCodeReview(promptName: string): Promise<void> {
    try {
        // 检查 git 仓库状态
        if (!await isGitRepository()) {
            logger.error('当前目录不是 git 仓库');
            return;
        }

        // 获取与主分支的代码差异
        const diff = await getGitDiff();
        if (!diff) {
            logger.info('没有发现代码变更，请确保：\n1. 当前分支有提交的改动\n2. 当前分支与主分支有差异');
            return;
        }

        // 检查 prompt 文件是否存在
        const commonPrompt = await loadPrompt('common');
        const specificPrompt = await loadPrompt(promptName);
        
        if (!commonPrompt || !specificPrompt) {
            logger.error(`无法加载 prompt 文件，请确认以下文件存在：\n1. prompts/common.txt\n2. prompts/${promptName}.txt`);
            return;
        }

        const fullPrompt = `${commonPrompt}\n${specificPrompt}\n\n以下是代码变更：\n${diff}`;

        // 获取 AI 反馈
        logger.info('正在分析代码变更...');
        const response = await getChatResponse(fullPrompt);
        
        if (!response) {
            logger.error('获取 AI 反馈失败，请检查网络连接和 AI 服务配置');
            return;
        }

        logger.info('代码审查结果：\n' + response);
    } catch (error) {
        if (error instanceof Error) {
            logger.error('代码审查过程中发生错误：', error.message);
        } else {
            logger.error('代码审查过程中发生未知错误');
        }
    }
} 