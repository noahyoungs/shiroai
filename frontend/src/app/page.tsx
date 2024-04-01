// app/redirect-to-home/page.js
import { redirect } from 'next/navigation';

export default function RedirectToHome() {
  redirect('/home');
}