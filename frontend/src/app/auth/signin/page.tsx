'use client';

import React, { useEffect } from 'react';
import { signIn } from 'next-auth/react';

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

  return <div>Redirecting to Login Page...</div>;
};

export default LoginPage;