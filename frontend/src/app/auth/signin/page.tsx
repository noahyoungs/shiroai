'use client';

import React, { useEffect } from 'react';
import { signIn } from 'next-auth/react';
import { Spinner } from '@nextui-org/react';

const LoginPage = () => {
  useEffect(() => {
    const signInUser = async () => {
      try {
        const result = await signIn('cognito', { redirect: true, callbackUrl: '/' });
        console.log('Sign-in result:', result);
      } catch (error) {
        console.error('Error during sign-in:', error);
      }
    };

    signInUser();
  }, []);

  return (
    <div className="flex items-center justify-center h-screen">
      <Spinner size="lg" color="primary" label="Redirecting to sign in page..."/>
    </div>
  )
};

export default LoginPage;