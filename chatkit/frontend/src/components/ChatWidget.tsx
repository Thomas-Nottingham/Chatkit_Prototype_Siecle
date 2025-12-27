

// import { useState } from "react";
// import { ChatKit, useChatKit } from "@openai/chatkit-react";
// import { CHATKIT_API_DOMAIN_KEY, CHATKIT_API_URL } from "../lib/config";



// export function ChatWidget() {
//   const [isOpen, setIsOpen] = useState(false);
//   const [message, setMessage] = useState("");
//   const [resetKey, setResetKey] = useState(0);

//   const { control, sendUserMessage, setComposerValue } = useChatKit({
//     api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },

    
//     composer: {
//       attachments: { enabled: false },
//       placeholder: "Type your question here...", // Custom placeholder
//     },
 
//   theme: {
//     density: "spacious",
//     colorScheme: "light",
//     color: {
//       grayscale: {
//         hue: 40,
//         tint: 9,
//         shade: "light" === "light" ? 4 : -4, // corrected conditional
//       },
//       accent: {
//         primary: "light" === "light" ? "#fdf5e6" : "#0f172a", // conditional fixed
//         level: 1,
//       },
//     },
//     radius: "round",
//   },
//   startScreen: {
//     greeting: "Welcome to Siecle, how can I help?",       // make sure GREETING is defined
//     // make sure STARTER_PROMPTS is defined
//   },
//   threadItemActions: {
//     feedback: false,

//   },

  
// });
//   // Send a chat message
//   const sendMessage = () => {
//     if (!message.trim()) return;
//     setComposerValue({ text: message });
//     sendUserMessage({ text: message });
//     setMessage("");
//   };

//   // Handle Enter key
//   const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
//     if (e.key === "Enter") sendMessage();
//   };


//   return (
//     <>
//       {isOpen && (
//         <div className="fixed bottom-20 right-4 z-50 h-[600px] w-[360px] rounded-xl shadow-xl overflow-hidden bg-[#fbf7f2] flex flex-col border border-[#e8dfd3]">
//           {/* Header */}
//           <div className="flex justify-between items-center px-4 py-3 border-b border-[#e8dfd3] bg-[#f6efe6]">
//             <div className="flex items-center gap-2">
//               <span className="text-lg">🧭</span>
//               <div>
//                 <h3 className="font-semibold text-sm text-[#3b2f2f]">Support Desk</h3>
//                 <p className="text-xs text-[#7a6f66]">Here to help</p>
//               </div>
//             </div>
//             <button
//               className="text-[#7a6f66] hover:text-[#3b2f2f] text-lg"
//               onClick={() => setIsOpen(false)}
//               aria-label="Close chat"
//             >
//               ✕
//             </button>
//           </div>

//           {/* Chat content */}
//           <div className="flex-1 overflow-hidden bg-[#fbf7f2] relative">
//             <ChatKit
//               key={resetKey}
//               control={control}
//               className="h-full w-full"
//               style={{ "--ck-feedback-display": "none" } as React.CSSProperties} // hide feedback
              
//             />

//             {/* Floating reset button inside chat panel */}
   

//             {/* Bottom input bar */}
//             <div className="absolute bottom-0 h-20 w-full px-3 py-2 bg-[#f6efe6] border-t border-[#e8dfd3] flex items-center gap-2 rounded-b-xl">
//               <input
//                 type="text"
//                 placeholder="Type your question here..."
//                 value={message}
//                 onChange={(e) => setMessage(e.target.value)}
//                 onKeyDown={handleKeyDown}
//                 className="flex-1 px-3 py-2 rounded-full border border-[#e8dfd3] bg-[#fff8f0] text-[#3b2f2f] focus:outline-none focus:ring-2 focus:ring-[#c9a66b]"
//               />
//               <button
//                 className="bg-[#c9a66b] p-2 rounded-full text-white hover:bg-[#b8955e] hover:shadow-lg transition-all"
//                 onClick={sendMessage}
//                 aria-label="Send message"
//               >
//                 ➤
//               </button>
//             </div>
//           </div>
//         </div>
//       )}

//       {/* Floating chat toggle button */}
//       <button
//         onClick={() => setIsOpen(!isOpen)}
//         className="fixed bottom-4 right-4 z-50 h-14 w-14 rounded-full bg-[#c9a66b] text-white shadow-lg hover:bg-[#b8955e] hover:shadow-xl transition-all flex items-center justify-center text-xl"
//         aria-label="Open support chat"
//       >
//         💬
//       </button>
//     </>
//   );
// }import { useState } from "react";import React, { useState, useEffect } from "react"; // Fixes: Cannot find name 'useState'import React from "react";import React, { useState } from "react"; // Explicit import for React and useState
import React from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_DOMAIN_KEY, CHATKIT_API_URL } from "../lib/config";

export function ChatWidget() {
  const [isOpen, setIsOpen] = React.useState(false);
  const [message, setMessage] = React.useState("");

  const { control, sendUserMessage } = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    
    // This matches the "widgets: { onAction: ... }" documentation
    widgets: {
      onAction: async (action: any) => {
        if (action.type === "open.url") {
          const url = action.payload?.url;
          if (url) {
            window.open(url, "_blank", "noopener,noreferrer");
          }
        }
      }
    },

    composer: {
      attachments: { enabled: false },
      placeholder: "Type your question here...",
    },
    theme: {
      density: "spacious",
      colorScheme: "light",
      color: {
        grayscale: { hue: 40, tint: 9, shade: 4 },
        accent: { primary: "#fdf5e6", level: 1 },
      },
      radius: "round",
    },
  } as any); // 'as any' prevents the TS 'known properties' error

  const sendMessage = () => {
    if (!message.trim()) return;
    sendUserMessage({ text: message });
    setMessage("");
  };

  return (
    <>
      {isOpen && (
        <div className="fixed bottom-20 right-4 z-50 h-[600px] w-[360px] rounded-xl shadow-xl overflow-hidden bg-[#fbf7f2] flex flex-col border border-[#e8dfd3]">
          <div className="flex-1 overflow-hidden relative">
            <ChatKit control={control} className="h-full w-full" />
            
            {/* Custom Input Bar */}
            <div className="absolute bottom-0 h-20 w-full px-3 py-2 bg-[#f6efe6] border-t border-[#e8dfd3] flex items-center gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                className="flex-1 px-3 py-2 rounded-full border bg-[#fff8f0]"
              />
              <button onClick={sendMessage} className="bg-[#c9a66b] p-2 rounded-full text-white">➤</button>
            </div>
          </div>
        </div>
      )}
      <button onClick={() => setIsOpen(!isOpen)} className="fixed bottom-4 right-4 z-50 h-14 w-14 rounded-full bg-[#c9a66b] text-white">
        💬
      </button>
    </>
  );
}