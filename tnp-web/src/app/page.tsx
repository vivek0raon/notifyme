import Link from "next/link";

export default function Home() {
  const jobsCalendarLink = "https://calendar.google.com/calendar/u/0?cid=fbcbe35fb7c1348253a9cc7b88653775bb3743b9720273921af87d230e050dc7@group.calendar.google.com";
  const notifsCalendarLink = "https://calendar.google.com/calendar/u/0?cid=49ba7feb079a98264dccaeb7fe39159df9a3c7d23fcdaaf8e8e018d06e66d801@group.calendar.google.com";

  return (
    <main className="min-h-screen bg-[#fafafa] text-neutral-900 font-sans selection:bg-blue-100 selection:text-blue-900">
      <div className="max-w-3xl mx-auto px-6 py-20 md:py-32 flex flex-col items-center text-center">
        
        {/* Hero Section */}
        <div className="space-y-6 mb-16">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm font-medium tracking-wide">
            Automated Placement Alerts
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-neutral-950 leading-tight">
            Never miss a <br className="hidden md:block"/> TnP deadline again.
          </h1>
          <p className="text-lg md:text-xl text-neutral-500 max-w-xl mx-auto leading-relaxed">
            Get instant push notifications and calendar alerts the moment a new company arrives at BIT Mesra.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="w-full max-w-sm mb-20 flex flex-col gap-4">
          <div className="text-left mb-2">
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-1">Step 1</p>
            <p className="text-neutral-700">Download the Google Calendar app</p>
          </div>
          <Link
            href="https://play.google.com/store/apps/details?id=com.google.android.calendar"
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-4 px-8 bg-white border-2 border-neutral-200 hover:border-neutral-300 text-neutral-900 font-semibold rounded-xl shadow-sm hover:shadow transition-all duration-200"
          >
            Get Google Calendar App
          </Link>

          <div className="text-left mt-6 mb-2">
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-1">Step 2</p>
            <p className="text-neutral-700">Add the Calendars you want</p>
          </div>
          
          <Link
            href={jobsCalendarLink}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-4 px-8 bg-neutral-950 hover:bg-neutral-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0 active:shadow-md"
          >
            🗓️ Subscribe to Jobs & Deadlines
          </Link>
          
          <Link
            href={notifsCalendarLink}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-4 px-8 bg-white border border-neutral-200 hover:border-neutral-300 text-neutral-900 font-semibold rounded-xl shadow-sm hover:shadow transition-all duration-200 mt-2"
          >
            🔔 Subscribe to Portal Notifications
          </Link>
          
          <p className="text-sm text-neutral-400 mt-4">
            Free forever. No login required.
          </p>
        </div>

        {/* Instructions */}
        <div className="w-full max-w-2xl bg-white border border-neutral-100 rounded-2xl p-8 md:p-12 shadow-sm text-left">
          <h2 className="text-2xl font-bold text-neutral-900 mb-8">How it works</h2>
          
          <div className="space-y-8">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-blue-50 text-blue-600 font-bold text-sm">
                1
              </div>
              <div>
                <h3 className="font-semibold text-neutral-900">Install Google Calendar</h3>
                <p className="text-neutral-500 mt-1">Make sure you have the Google Calendar app installed on your phone and notifications are enabled.</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-blue-50 text-blue-600 font-bold text-sm">
                2
              </div>
              <div>
                <h3 className="font-semibold text-neutral-900">Subscribe</h3>
                <p className="text-neutral-500 mt-1">Click the buttons above. They will open your calendar and ask you to add the shared calendars.</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-blue-50 text-blue-600 font-bold text-sm">
                3
              </div>
              <div>
                <h3 className="font-semibold text-neutral-900">You're all set!</h3>
                <p className="text-neutral-500 mt-1">Whenever a new company is posted, you'll get an instant push notification on your phone, plus a 24-hour reminder before the deadline.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-24 text-sm text-neutral-400">
          Built for the students of BIT Mesra.
        </footer>
      </div>
    </main>
  );
}
