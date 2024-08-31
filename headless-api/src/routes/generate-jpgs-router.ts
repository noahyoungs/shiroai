// headless-service/src/routes/generate-pdf-router.ts
import express from "express";
import { generateJPGsHandler } from "../utils/generate-jpgs";

const router = express.Router();

router.post("/:presentationId/jpg", generateJPGsHandler);

export default router;