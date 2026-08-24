/* Signal Archive password reset: one-time token and replacement password are never persisted client-side. */
import { AccountForm } from "../../components/account-form";
export default function ResetPasswordPage() { return <AccountForm mode="reset"/>; }
