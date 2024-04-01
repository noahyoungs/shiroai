// interface.tsx
"use client"
import { Textarea } from "@nextui-org/react";
import { Button } from "@nextui-org/react";
import { Spacer } from "@nextui-org/react";
import { useRouter } from 'next/navigation';

interface InterfaceProps {
    topic: string;
    audience: string;
    goal: string;
    setTopic: (topic: string) => void;
    setAudience: (targetAudience: string) => void;
    setGoal: (goal: string) => void;
    block: boolean;
    redirectPath: string;
    presentationID: string;
}

export default function Interface({ topic, audience, goal, setTopic, setAudience, setGoal, block, redirectPath }: InterfaceProps) {
    const router = useRouter();
    return (
        <div className="p-5 flex flex-col">
            <h1>Your Presentation Idea</h1>
            <Spacer y={6} />
            <h3>Presentation Topic</h3>
            <Textarea
                aria-label="Topic"
                placeholder="Enter your description"
                className=""
                value={topic}
                onValueChange={setTopic}
                isDisabled={block}

            />
            <Spacer y={6} />
            <h3>Target Audience</h3>
            <Textarea
                aria-label="Target Audience"
                placeholder="Enter your description"
                className=""
                value={audience}
                onValueChange={setAudience}
                isDisabled={block}
            />
            <Spacer y={6} />
            <h3>Presentation Goal</h3>
            <Textarea
                aria-label="Goal"
                placeholder="Enter your description"
                className=""
                value={goal}
                onValueChange={setGoal}
                isDisabled={block}
            />
            <Spacer y={6} />
            <Button
                color={"primary"}
                onClick={() => {
                    router.push(redirectPath);
                  }}
                isDisabled={block || !topic || !audience || !goal}
                // className="w-fit"
            >  
                Proceed to Next Step
            </Button>
        </div>
    );
}