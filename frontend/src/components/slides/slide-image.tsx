'use client';

import Image from 'next/image';
import { useEffect, useState } from 'react';
import { Image as ImageData } from '@/utils/slide-types';
import { Image as NextUIImage } from "@nextui-org/react";

const getImage = (key: string) => {
    return fetch(`http://localhost:3000/api/images?key=${encodeURIComponent(key)}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error('Failed to fetch image');
            }
            return response.json(); // Parse the response as JSON
        })
        .catch((error) => {
            console.error('Error fetching image:', error);
        });
};

type SlideImageProps = {
    image?: ImageData;
};

export function SlideImage({ image }: SlideImageProps) {
    const [imageUrl, setImageUrl] = useState<string | undefined>(undefined);

    useEffect(() => {
        if (image) {
            if (image.url) {
                setImageUrl(image.url);
            } else if (image.s3_key) {
                getImage(image.s3_key).then((data) => {
                    if (typeof data === 'string') {
                        setImageUrl(data);
                    } else if (typeof data === 'object' && data.url) {
                        setImageUrl(data.url);
                    }
                });
            }
        }
    }, [image]);

    if (!image) {
        return null; // or return a placeholder or error message
    }

    let width: number;
    let height: number = 1080;

    switch (image.shape) {
        case 'full':
            width = 1920;
            break;
        case 'half':
            width = 960;
            break;
        case 'square':
            width = 1080;
            break;
        default:
            width = 1920;
    }

    return (
        <div>
            {imageUrl ? (
                <NextUIImage
                    src={imageUrl}
                    alt={image.alt}
                    width={width}
                    height={height}
                    classNames={{
                        img: 'rounded-none',
                        wrapper: 'rounded-none',
                    }}
                />
            ) : (
                <p>Loading image...</p>
            )}
        </div>
    );
}