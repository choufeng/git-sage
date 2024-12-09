import { handleCodeReview } from './codeReview';

export function registerCommands(program: Command) {
    program
        .command('cr')
        .description('检查当前分支与主分支的代码差异')
        .argument('[prompt]', '使用的prompt模板，默认为ccr')
        .action(async (prompt = 'ccr') => {
            await handleCodeReview(prompt);
        });
} 