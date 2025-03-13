import "./globals.css";

export const metadata = {
  title: "GitHub Scraper",
  description: "Scrape GitHub repositories and users with ease.",
  icons: {
    icon: "/favicon.ico", 
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
          {children}
      </body>
    </html>
  );
}