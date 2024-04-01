import React from 'react';

const steps = ["Ideate", "Configure", "Outline", "Theme", "Edit", "Narrate", "Render", "Publish"] as const;

type Step = typeof steps[number];

type GenerationProgressProps = {
    currentStep: Step;
    currentStepPercentage?: number;
};

export default function GenerationProgress({ currentStep, currentStepPercentage = 50 }: GenerationProgressProps) {
    const currentStepIndex = steps.findIndex(step => step === currentStep);

    const individualStepPercentage = 100 / steps.length;
    const progressBarPercentage = (currentStepIndex * individualStepPercentage) + (individualStepPercentage * currentStepPercentage / 100);

    // Inline style for grid layout
    const gridStyle = {
        gridTemplateColumns: `repeat(${steps.length}, minmax(0, 1fr))`,
        alignItems: 'center'
    };

    return (
        <div className={"w-full mt-0 pt-0"}>
            <h4 className="sr-only">Status</h4>
                <div className="overflow-hidden  bg-gray-200">
                    <div className="h-2  bg-indigo-600" style={{ width: `${progressBarPercentage}%` }} />
                </div>
                <div className="mt-4 grid gap-4 text-sm font-medium text-black align-center" style={gridStyle}>
                    {steps.map((step, index) => (
                        <div
                            key={index}
                            // Modify this line to change text color for completed steps
                            className={`text-center ${index < currentStepIndex ? 'text-indigo-600' : index === currentStepIndex ? 'text-indigo-600 font-semibold text-base' : 'text-gray-600'}`}
                        >
                            {step}
                        </div>
                    ))}
                </div>
        </div>
    );
}
