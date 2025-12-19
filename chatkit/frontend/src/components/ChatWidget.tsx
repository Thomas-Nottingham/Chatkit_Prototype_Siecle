import { useState } from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_DOMAIN_KEY, CHATKIT_API_URL } from "../lib/config";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);

  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    composer: { attachments: { enabled: false } },
  });

  return (
    <>
      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 z-50 h-[600px] w-[360px] rounded-2xl shadow-lg overflow-hidden bg-white dark:bg-slate-900 flex flex-col">
          <div className="flex justify-between items-center p-3 border-b bg-gray-100 dark:bg-slate-800">
            <h3 className="font-bold text-lg">Chat</h3>
            <button
              className="text-gray-500 hover:text-gray-800"
              onClick={() => setIsOpen(false)}
            >
              ✕
            </button>
          </div>
          {/* Chat content */}
          <div className="flex-1 overflow-hidden">
            <ChatKit control={chatkit.control} className="h-full w-full" />
          </div>
        </div>
      )}

      {/* Floating button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 z-50 h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 flex items-center justify-center text-2xl"
      >
        💬
      </button>
    </>
  );
}
