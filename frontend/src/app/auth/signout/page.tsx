'use client'; // This makes the component a client component
import { useEffect } from 'react';
import { Spinner } from '@nextui-org/react';
import signOutAction from "@/actions/sign-out-action.ts";
import { useRouter } from 'next/navigation';

export default function SignOutPage() {
    const router = useRouter(); 
  useEffect(() => {
    // Define a function to handle sign out
    const performSignOut = async () => {
      try {
        await signOutAction(); // Call the server action
        router.push('/'); // Redirect to the home page
      } catch (error) {
        console.error('Error during sign-out:', error);
      }
    };

    performSignOut();
  }, []); // Empty dependency array to mimic componentDidMount behavior

  return (
    <div className="flex items-center justify-center h-screen">
      <Spinner size="lg" color="primary" label="Signing you out..." />
    </div>
  );
}
