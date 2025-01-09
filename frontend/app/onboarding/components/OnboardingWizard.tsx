"use client";

import { useState } from "react";
import { Candidate, CandidateRequest, CandidateSchema, Interviewer } from "../types"
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

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
        <Form {...form} >
            <form className="flex flex-col gap-4 justify-center w-1/2" onSubmit={form.handleSubmit(handleFormSubmit)}>
                <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Name</FormLabel>
                            <FormControl>
                                <Input placeholder="Candidate Name" {...field} />
                            </FormControl>
                            <FormDescription>
                                This is the name of the candidate.
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
                            <FormLabel>Email</FormLabel>
                            <FormControl>
                                <Input placeholder="Candidate Email" {...field} />
                            </FormControl>
                            <FormDescription>
                                This is the email of the candidate.
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
                            <FormLabel>Phone Number</FormLabel>
                            <FormControl>
                                <Input placeholder="Candidate Phone Number" {...field} />
                            </FormControl>
                            <FormDescription>
                                This is the phone number of the candidate.
                            </FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <Button disabled={isLoading} type="submit">
                    {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Submit
                </Button>
            </form>
        </Form>
    )
}

const createCandidate = async (data: CandidateRequest) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v3/interview/candidate`, {
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
        const candidate = CandidateSchema.parse(await response.json());
        return candidate;
    } catch (error) {
        console.error(error);
        throw new Error('Failed to parse candidate');
    }
}

const OnboardingWizard = () => {
    const [candidateData, setCandidateData] = useState<CandidateRequest | null>(null);

    const handleSubmit = async (data: z.infer<typeof formSchema>) => {
        // Simulate API call
        const candidateRequest: CandidateRequest = {
            name: data.name,
            email: data.email,
            phone_number: data.phone_number,
        }
        setCandidateData(candidateRequest);
        const candidate = await createCandidate(candidateRequest);
        console.log(candidate);
    }

  return (
    <div className="flex flex-col w-full items-center ">
        <UserProfileForm onSubmit={handleSubmit} />
    </div>
  )
}

export default OnboardingWizard