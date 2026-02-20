/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost', 's3.amazonaws.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Disable static export for dynamic app with authentication
  output: undefined,
  trailingSlash: false,
  experimental: {
    serverComponentsExternalPackages: [],
  },
}

module.exports = nextConfig
