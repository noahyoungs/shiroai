import NextAuth from "next-auth";
import Cognito from "next-auth/providers/cognito"

export const { auth, handlers, signIn, signOut } = NextAuth({
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    Cognito({
      clientId: process.env.NEXT_PUBLIC_COGNITO_ID,
      checks: ["nonce"],
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
    async session({ session, token, user }) {
      session.user.cognito_sub = token.cognito_sub!;      
      return session
    },
    async jwt({ token, account, profile }) {
      // Persist the OAuth access_token and or the user id to the token right after signin
      if (account) {
        token.accessToken = account.access_token
        token.cognito_sub = profile.sub
      }
      return token
  }
}
})
