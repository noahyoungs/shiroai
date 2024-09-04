'use server';
import { signOut } from "@/auth.ts"


export default async function SignOutAction() {
      await signOut();
    }