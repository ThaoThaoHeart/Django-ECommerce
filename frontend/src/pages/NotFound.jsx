import { PageError } from "../components/Status";

export default function NotFound() {
  return <PageError error={{ response: { status: 404 } }} />;
}
