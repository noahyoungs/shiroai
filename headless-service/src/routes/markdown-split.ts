// headless-service/src/routes/markdown-split.ts
import { Router } from 'express';
import { splitMarkdown } from '../utils/split-markdown';

const router = Router();

router.post('/split', (req, res) => {
  const { markdown } = req.body;
  if (!markdown) {
    return res.status(400).json({ error: 'Markdown content is required' });
  }

  const [firstPart, secondPart] = splitMarkdown(markdown);

  return res.json({ firstPart, secondPart });
});

export default router;
