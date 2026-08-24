const production = process.env.UHT_ENVIRONMENT === "production";
const required = ["NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_SITE_URL"];

if (!production) {
  console.log(JSON.stringify({ status: "not-configured", evidence: "UHT_ENVIRONMENT is not production; production browser URL validation was not requested" }));
  process.exit(0);
}

const errors = [];
for (const name of required) {
  const value = process.env[name];
  if (!value) {
    errors.push(`${name} is required`);
    continue;
  }
  try {
    const parsed = new URL(value);
    if (parsed.protocol !== "https:" || parsed.username || parsed.password || parsed.search || parsed.hash) errors.push(`${name} must be a credential-free HTTPS origin or API base URL`);
  } catch {
    errors.push(`${name} must be a valid URL`);
  }
}

if (errors.length) {
  console.log(JSON.stringify({ status: "blocked", errors }));
  process.exit(2);
}
console.log(JSON.stringify({ status: "validated", evidence: "public production browser URLs are explicit HTTPS values" }));
