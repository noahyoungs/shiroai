import NextAuth from "next-auth";
import Cognito from "next-auth/providers/cognito"

export const { auth, handlers, signIn, signOut } = NextAuth({
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    Cognito({
      clientId: process.env.NEXT_PUBLIC_COGNITO_ID,
      checks: ["nonce"],
      // Step 1 below: parameters are taken from cognito and put in the profile (sub is included by default)
      profile(profile) {
        return {
          name: profile.name,
          email: profile.email,
          image: profile.picture,
        }
      },
    }
    )
  ],
  pages: {
    signIn: "/auth/signin",
    signOut: "/auth/signout",
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
    // Step 2 below: parameters are taken from the profile and put in the token
    async jwt({ token, account, profile }) {
      if (!profile) return token;

      // Persist the OAuth access_token and or the user id to the token right after signin
      if (account) {
        token.accessToken = account.access_token
        token.cognito_sub = profile.sub
      }
      return token
    },
    // Step 3 below: parameters are taken from the token and put in the user session
    async session({ session, token, user }) {
      session.user.id = token.cognito_sub! as string;
      return session
    }
  }
})
