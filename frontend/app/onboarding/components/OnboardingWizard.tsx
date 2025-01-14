"use client";

import { useEffect, useRef, useState } from "react";
import { Candidate, CandidateRequest, CandidateSchema, Interviewer, InterviewerSchema, InterviewSession, InterviewSessionSchema } from "../types"
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const formSchema = z.object({
    name: z.string().min(1, { message: "Name is required" }),
    email: z.string().email({ message: "Invalid email address" }),
    phone_number: z.string().min(1, { message: "Phone number is required" }),
});

const UserProfileForm = ({onSubmit}: {onSubmit: (data: z.infer<typeof formSchema>) => void}) => {
    const [isLoading, setIsLoading] = useState(false);
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            name: "",
            email: "",
            phone_number: "",
        },
    });

    const handleFormSubmit = async (data: z.infer<typeof formSchema>) => {
        setIsLoading(true);
        try {
            await onSubmit(data);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col w-full items-center min-w-1/3">
            <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-lg">
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-gray-900">Register for Interview</h2>
                    <p className="mt-2 text-sm text-gray-600">Please fill in your details below</p>
                </div>
                <Form {...form}>
                    <form className="space-y-6" onSubmit={form.handleSubmit(handleFormSubmit)}>
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel className="text-gray-700">Full Name</FormLabel>
                                    <FormControl>
                                        <Input className="w-full" placeholder="John Doe" {...field} />
                                    </FormControl>
                                    <FormDescription className="text-gray-500 text-sm">
                                        Enter your full legal name
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="email"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel className="text-gray-700">Email Address</FormLabel>
                                    <FormControl>
                                        <Input className="w-full" placeholder="you@example.com" {...field} />
                                    </FormControl>
                                    <FormDescription className="text-gray-500 text-sm">
                                        We'll use this to send interview details
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="phone_number"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel className="text-gray-700">Phone Number</FormLabel>
                                    <FormControl>
                                        <Input className="w-full" placeholder="+1 (555) 000-0000" {...field} />
                                    </FormControl>
                                    <FormDescription className="text-gray-500 text-sm">
                                        For interview-related communications
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Button 
                            disabled={isLoading} 
                            type="submit"
                            className="w-full py-2 transition-colors"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Registering...
                                </>
                            ) : (
                                'Register'
                            )}
                        </Button>
                    </form>
                </Form>
            </div>
        </div>
    )
}

const createCandidate = async (data: CandidateRequest, interviewer_id: string) => {
    const params = new URLSearchParams();
    params.set('interviewer_id', interviewer_id);
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v3/interview/candidate?${params.toString()}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error('Failed to create candidate');
    }
    try {
        const interviewSession: InterviewSession = InterviewSessionSchema.parse(await response.json());
        return interviewSession;
    } catch (error) {
        console.error(error);
        throw new Error('Failed to parse interview session');
    }
}

const getInterviewer = async (interviewer_id: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v3/interview/${interviewer_id}`);
    if (!response.ok) {
        throw new Error('Failed to get interviewer');
    }
    try {
        const interviewer: Interviewer = InterviewerSchema.parse(await response.json());
        return interviewer;
    } catch (error) {
        console.error(error);
        throw new Error('Failed to parse interviewer');
    }
}

type InterviewDetailsProps = {
    interviewer_id: string;
    handleClick: () => void;
}

const InterviewDetails = ({interviewer_id, handleClick}: InterviewDetailsProps) => {
    const [interviewer, setInterviewer] = useState<Interviewer | null>(null);
    useEffect(() => {
        getInterviewer(interviewer_id).then(setInterviewer);
    }, [interviewer_id]);
    
    return (
        <div className="relative flex flex-col gap-8 w-full max-w-4xl p-8">
            <h1 className="absolute text-2xl font-bold">Interview Details</h1>
            
            <Button onClick={handleClick} className="sticky top-2 self-end">
            Start Interview
            </Button>
            <div className="flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                    <h2 className="text-lg font-semibold">Interviewer ID</h2>
                    <div className="prose prose-sm">
                        <code>{interviewer_id}</code>
                    </div>
                </div>

                <div className="flex flex-col gap-2">
                    <h2 className="text-lg font-semibold">Job Description</h2>
                    <div className="prose prose-sm max-w-none">
                        <Markdown>{interviewer?.job_description || ''}</Markdown>
                    </div>
                </div>
            </div>

        </div>
    )
}

const ProvidePermissions = ({ onPermissionsGranted }: { onPermissionsGranted: () => void }) => {
    const [permissions, setPermissions] = useState({
        microphone: false,
        camera: false,
        screen: false
    });
    const [error, setError] = useState<string | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const [stream, setStream] = useState<MediaStream | null>(null);

    const requestMicrophonePermission = async () => {
        try {
            await navigator.mediaDevices.getUserMedia({ audio: true });
            setPermissions(prev => ({ ...prev, microphone: true }));
        } catch (err) {
            setError('Please allow access to your microphone');
        }
    };

    const requestCameraPermission = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
                await videoRef.current.play();
            }
            setPermissions(prev => ({ ...prev, camera: true }));
        } catch (err) {
            console.error('Camera permission error:', err);
            setError('Please allow access to your camera');
        }
    };

    const requestScreenPermission = async () => {
        try {
            await navigator.mediaDevices.getDisplayMedia({ video: true });
            setPermissions(prev => ({ ...prev, screen: true }));
        } catch (err) {
            setError('Please allow screen sharing access');
        }
    };

    useEffect(() => {
        if (permissions.microphone && permissions.camera && permissions.screen) {
            onPermissionsGranted();
        }
    }, [permissions, onPermissionsGranted]);

    useEffect(() => {
        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [stream]);

    return (
        <div className="flex flex-col items-center gap-6 p-8">
            <h2 className="text-2xl font-bold">Device Permissions</h2>
            <p className="text-gray-600 text-center max-w-md">
                Please grant the following permissions to continue:
            </p>
            
            {error && <p className="text-red-500">{error}</p>}
            
            <div className="flex flex-col gap-4">
                <div className="flex items-center gap-2">
                    <Button 
                        onClick={requestMicrophonePermission}
                        disabled={permissions.microphone}
                        variant={permissions.microphone ? "outline" : "default"}
                    >
                        {permissions.microphone ? "✓ Microphone" : "Enable Microphone"}
                    </Button>
                </div>

                <div className="flex items-center gap-2">
                    <Button 
                        onClick={requestCameraPermission}
                        disabled={permissions.camera}
                        variant={permissions.camera ? "outline" : "default"}
                    >
                        {permissions.camera ? "✓ Camera" : "Enable Camera"}
                    </Button>
                </div>

                <div className="flex items-center gap-2">
                    <Button 
                        onClick={requestScreenPermission}
                        disabled={permissions.screen}
                        variant={permissions.screen ? "outline" : "default"}
                    >
                        {permissions.screen ? "✓ Screen Sharing" : "Enable Screen Sharing"}
                    </Button>
                </div>
            </div>

                <div className="mt-4 rounded-lg overflow-hidden border border-gray-200">
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-[320px] h-[240px] object-cover"
                        style={{ transform: 'scaleX(-1)' }}
                        onLoadedMetadata={(e) => e.currentTarget.play()}
                    />
                </div>
        </div>
    );
};

const OnboardingWizard = ({interviewer_id}: {interviewer_id: string}) => {
    const [candidateData, setCandidateData] = useState<CandidateRequest | null>(null);
    const [interviewSession, setInterviewSession] = useState<InterviewSession | null>(null);
    const [stage, setStage] = useState<"interview_details" | "user_profile" | "provide_permissions">("interview_details");
    const router = useRouter();

    const handleSubmit = async (data: z.infer<typeof formSchema>) => {
        // Simulate API call
        const candidateRequest: CandidateRequest = {
            name: data.name,
            email: data.email,
            phone_number: data.phone_number,
        }
        setCandidateData(candidateRequest);
        const interviewSession = await createCandidate(candidateRequest, interviewer_id);
        setInterviewSession(interviewSession);
        console.log(interviewSession);
        setStage("provide_permissions");
    }

    const handlePermissionsGranted = () => {
        if (interviewSession) {
            router.push(`/interview?interview_session_id=${interviewSession._id}`);
        }
        console.log(interviewSession);
    };

    const renderStage = (stage: "interview_details" | "user_profile" | "provide_permissions", interviewer_id: string) => {  
        switch (stage) {
            case "interview_details":
                return <InterviewDetails interviewer_id={interviewer_id} handleClick={() => setStage("user_profile")} />;
            case "user_profile":
                return <UserProfileForm onSubmit={handleSubmit} />;
            case "provide_permissions":
                return <ProvidePermissions onPermissionsGranted={handlePermissionsGranted} />;
        }
    }

  return (
    <div className="flex flex-col w-full items-center min-h-screen justify-center" >
        {renderStage(stage, interviewer_id)}
    </div>
  )
}

export default OnboardingWizard;