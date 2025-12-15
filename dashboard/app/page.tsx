import { redirect } from "next/navigation";

export default function Home() {
  // Redirect to trips page
  redirect("/trips");
}

