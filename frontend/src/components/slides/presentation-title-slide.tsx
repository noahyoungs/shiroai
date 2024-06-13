// import { PresentationTitleSlide } from "@/utils/slide-types";
// import { SlideImage } from "./slide-image";

// type PresentationTitleSlideComponentProps = {
//     slide: PresentationTitleSlide;
// };

// export function PresentationTitleSlideComponent({ slide }: PresentationTitleSlideComponentProps) {
//     return (
//         <div className="relative overflow-hidden height-auto bg-foreground/5 text-foreground box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-video flex-none">
//             <h1 className="absolute mx-12 bottom-10 z-[21] text-background/90">{slide.slide_title}</h1>
//             <SlideImage image={slide.image} />
//             <div className="absolute inset-0">
//                 <div
//                     className="absolute inset-0 bg-gradient-to-t from-foreground/80 via-transparent to-transparent z-20"
//                 ></div>      
//                 </div>
//         </div>
//     );
// }
"use client"

import { PresentationTitleSlide } from "@/utils/slide-types";
import { SlideImage } from "./slide-image";
import { updateSlide } from "@/actions/slides-actions"
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Textarea, Button, useDisclosure } from "@nextui-org/react";
import { useState } from "react";

type PresentationTitleSlideComponentProps = {
    slide: PresentationTitleSlide;
    presentationID: string;
    fetchSlide: (slideID: string) => void;
    setBlockArrowKeys: (block: boolean) => void;
};

export function PresentationTitleSlideComponent({ slide, presentationID, fetchSlide, setBlockArrowKeys }: PresentationTitleSlideComponentProps) {
    const [tempTitle, setTempTitle] = useState(slide.slide_title);
    const [loading, setLoading] = useState(false)
    const { isOpen, onOpen, onOpenChange } = useDisclosure();
    return (
        <>
            <Modal isOpen={isOpen} onOpenChange={onOpenChange} size="4xl">
                <ModalContent>
                    {(onClose) => (
                        <>
                            <ModalHeader className="flex flex-col gap-1">Edit Presentation Title</ModalHeader>
                            <Textarea
                                label="Presentation Title"
                                placeholder="My Wonderful Presentation"
                                className="w-[90%] mx-auto"
                                variant="underlined"
                                minRows={1}
                                value={tempTitle}
                                onValueChange={setTempTitle}
                                autoFocus
                            />
                            <ModalBody>

                            </ModalBody>
                            <ModalFooter>
                                <Button color="danger" variant="light" onPress={onClose}>
                                    Close
                                </Button>
                                <Button
                                    color="primary"
                                    onPress={async () => {
                                        if (tempTitle !== slide.slide_title) {
                                            setLoading(true)
                                            await updateSlide(presentationID, { ...slide, slide_title: tempTitle })
                                            await fetchSlide(slide.id)
                                            setLoading(false)
                                        }
                                        onClose()
                                    }}
                                    isLoading={loading}
                                >
                                    Save
                                </Button>
                            </ModalFooter>
                        </>
                    )}
                </ModalContent>
            </Modal>
            <div className="relative overflow-hidden height-auto bg-foreground/5 text-foreground box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-video flex-none">
                <h1
                    className="absolute mx-12 bottom-10 z-[21] text-background/90 cursor-text"
                    onClick={onOpen}
                >
                    {slide.slide_title}
                </h1>
                <SlideImage image={slide.image} />
                <div className="absolute inset-0">
                    <div
                        className="absolute inset-0 bg-gradient-to-t from-foreground/80 via-transparent to-transparent z-20"
                    ></div>
                </div>
            </div>
        </>
    );
}