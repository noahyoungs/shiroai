import NextAuth from "next-auth";
import Cognito from "next-auth/providers/cognito"
import { CognitoIdentityProviderClient, AdminUserGlobalSignOutCommand } from "@aws-sdk/client-cognito-identity-provider";
import type { JWT } from "next-auth/jwt"; // Import JWT type from next-auth

// Define a type for the token structure you receive in the signOut event
type UserToken = {
  name: string;
  email: string;
  sub: string; // User's Cognito ID
  iat: number;
  exp: number;
  jti: string;
};

// Initialize the Cognito Identity Provider client
const cognitoClient = new CognitoIdentityProviderClient();

// Function to handle global sign-out from Cognito
async function handleGlobalSignOut(sub: string): Promise<void> {
  try {
    const params = {
      UserPoolId: process.env.COGNITO_USER_POOL_ID!,
      Username: sub, // The user's Cognito ID (sub)
    };

    const command = new AdminUserGlobalSignOutCommand(params);

    // Initiating global sign-out
    await cognitoClient.send(command);
    console.log("Successfully signed out globally from Cognito");
  } catch (error) {
    console.error("Error signing out globally:", error);
  }
}

export const { auth, handlers, signIn, signOut } = NextAuth({
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    Cognito({
      async profile(profile) {
        return {
          sub: profile.sub,
          name: profile.name,
          email: profile.email,
          picture: profile.picture,
        };
      }
    }),
  ],
  pages: {
    signIn: "/auth/signin",
  },
  cookies: {
    sessionToken: {
      name: `__Secure-next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: "none",
        path: "/",
        secure: true,
      },
    },
  },
  callbacks: {
    async session({ session, token, user }) {
      // Send properties to the client, like an access_token and user id from a provider.
      session.user.id = token.sub!;      
      return session
    }
  }
});
