// Stability
import model3DImage from '/public/style-images/3d-model.webp';
import animeImage from '/public/style-images/anime.webp';
import comicBookImage from '/public/style-images/comic-book.webp';
import fantasyArtImage from '/public/style-images/fantasy-art.webp';
import lineArtImage from '/public/style-images/line-art.webp';
import modelingCompoundImage from '/public/style-images/modeling-compound.webp';
import origamiImage from '/public/style-images/origami.webp';
import pixelArtImage from '/public/style-images/pixel-art.webp';
import analogFilmImage from '/public/style-images/analog-film.webp';
import cinematicImage from '/public/style-images/cinematic.webp';
import isometricImage from '/public/style-images/isometric.webp';
import lowPolyImage from '/public/style-images/low-poly.webp';
import neonPunkImage from '/public/style-images/neon-punk.webp';
import photographicImage from '/public/style-images/photographic.webp';
import defaultImage from '/public/style-images/default.webp';
// Dalle
import vividImage from '/public/style-images/vivid.webp';
import naturalImage from '/public/style-images/natural.webp';

export const stabilityStyles = [
    { name: "Default", value: "default", description: "The model will pick and appropriate style based on your prompt.", image: defaultImage },
    { name: "3D Model", value: "3d-model", description: "Realistic or semi-realistic images with depth, perspective, and detailed textures, often created using 3D modeling software.", image: model3DImage },
    { name: "Analog Film", value: "analog-film", description: "Images that mimic the grain, color saturation, and imperfections of traditional film photography. Has a 1930s-1960s film aesthetic.", image: analogFilmImage },
    { name: "Anime", value: "anime", description: "Stylized, colorful, and often exaggerated imagery with influences from Japanese animation.", image: animeImage },
    { name: "Cinematic", value: "cinematic", description: "Dramatic images with careful attention to lighting, composition, and color grading, resembling movie stills. Has a 1970s-1990s film aesthetic.", image: cinematicImage },
    { name: "Comic Book", value: "comic-book", description: "Bold, graphic imagery with strong lines, vibrant colors, and often text elements like speech bubbles or captions.", image: comicBookImage },
    { name: "Fantasy Art", value: "fantasy-art", description: "Imaginative and often otherworldly imagery featuring mythical creatures, magical landscapes, and fantastical elements.", image: fantasyArtImage },
    { name: "Isometric", value: "isometric", description: "3D representations in a 2D format with a consistent angle, often used for technical and architectural drawings.", image: isometricImage },
    { name: "Line Art", value: "line-art", description: "Artistic sketches or simple and clean images created using lines, often in black and white or minimal color.", image: lineArtImage },
    { name: "Low Poly", value: "low-poly", description: "Simplified, geometric images with flat shading and minimal detail, often resembling early 3D computer graphics.", image: lowPolyImage },
    { name: "Modeling Compound", value: "modeling-compound", description: "Images resembling clay or sculpted figures, often with a tactile, handcrafted look.", image: modelingCompoundImage },
    { name: "Neon Punk", value: "neon-punk", description: "Bright, vibrant imagery with neon colors and a punk aesthetic, often featuring futuristic or dystopian elements.", image: neonPunkImage },
    { name: "Origami", value: "origami", description: "Images inspired by the art of paper folding, often with clean lines and geometric shapes.", image: origamiImage },
    { name: "Photographic", value: "photographic", description: "Realistic images that resemble traditional photography.", image: photographicImage },
    { name: "Pixel Art", value: "pixel-art", description: "Images created using small, discrete pixels, reminiscent of early video game graphics.", image: pixelArtImage },
];

export const dalleStyles = [
    { name: "Vivid", value: "default", description: "Hyper-real and dramatic images, often with a surreal or dreamlike quality.", image: vividImage },
    { name: "Natural", value: "natural", description: "Natural, less hyper-real looking images, photorealistic look.", image: naturalImage }
];
