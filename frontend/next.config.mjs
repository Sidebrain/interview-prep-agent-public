const nextConfig = {
  output: "standalone",
};

export default async (phase, { defaultConfig }) => {
  return nextConfig;
};
// module.exports = async (phase, { defaultConfig }) => {
//   /** @type {import('next').NextConfig} */
//   const nextConfig = {
//     output: "standalone",
//     //   async rewrites() {
//     //     return [
//     //       {
//     //         source: "/__/auth/:path*",
//     //         destination: "http://localhost:8000/api/v1/auth/:path*", // Adjust if your FastAPI server runs on a different port
//     //       },
//     //     ];
//     //   },
//   };
//   return nextConfig;
// };

// export default module;
