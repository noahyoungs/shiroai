// headless-service/src/routes/generate-pdf-router.ts
import express from "express";
import { generatePDF } from "../utils/generate-pdf";

const router = express.Router();

router.post("/:presentationId/pdf", generatePDF);

export default router;