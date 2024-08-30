// headless-service/src/routes/generate-pdf-router.ts
import express from "express";
import { generateJPGs } from "../utils/generate-jpgs";

const router = express.Router();

router.post("/:presentationId/jpg", generateJPGs);

export default router;