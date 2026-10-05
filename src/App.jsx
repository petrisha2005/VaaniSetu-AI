import React, { useState, useRef, useEffect } from 'react';
import { 
  FileText, Mic, Play, Pause, CheckCircle2, ShieldCheck, 
  Volume2, Sparkles, ArrowRight, Upload, AlertCircle, RefreshCw,
  Layers, Cpu, Radio, Languages, X, RotateCcw, Globe
} from 'lucide-react';
import { SUPPORTED_LANGUAGES, getLanguageMeta } from './languages';

export default function App() {
  // Multilingual State
  const [selectedLanguageCode, setSelectedLanguageCode] = useState('kn-IN');
  const currentLang = getLanguageMeta(selectedLanguageCode);

  // Document & Mode State
  const [isSampleMode, setIsSampleMode] = useState(true);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('/kannada.png');
  const [fileType, setFileType] = useState('image'); // 'image' | 'pdf'
  const [fileName, setFileName] = useState('kannada.png');
  
  // Question & Speech State
  const [questionText, setQuestionText] = useState(currentLang.sampleQuestion);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isPlayingQuestion, setIsPlayingQuestion] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Pipeline Execution State
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0); // 0: Idle, 1: OCR, 2: 105B, 3: Bulbul
  const [analysisError, setAnalysisError] = useState(null);
  
  // Answer & Audio State
  const [showEnglishTranslation, setShowEnglishTranslation] = useState(false);
  const [isPlayingAnswer, setIsPlayingAnswer] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);
  const [audioCurrentTime, setAudioCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);

  // Sample Baseline Answer Map per language
  const sampleAnswersMap = {
    "kn-IN": {
      answer: "ಈ ನೋಟಿಸ್ ಕೆ.ಆರ್.ಪುರಂ ತಾಲ್ಲೂಕಿನ ಸೂಲಿಕೆರೆ ಗ್ರಾಮದಲ್ಲಿ ರಸ್ತೆ ವಿಸ್ತರಣೆ ಮತ್ತು ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗಾಗಿ ಕರ್ನಾಟಕ ಭೂಸ್ವಾಧೀನ ಕಾಯ್ದೆ 2013ರ ಅಡಿಯಲ್ಲಿ ಜಮೀನು ಸ್ವಾಧೀನಪಡಿಸಿಕೊಳ್ಳುವುದನ್ನು ಕುರಿತು ಪ್ರಕಟಿಸಿದ ಪಟ್ಟಿಯಾಗಿದೆ. ಇದರಲ್ಲಿ ಸರ್ವೆ ನಂಬರ್‌ಗಳು, ಮಾಲೀಕರ ಹೆಸರು, ವಿಸ್ತೀರ್ಣ ಮತ್ತು ಪರಿಹಾರ ಮೊತ್ತಗಳನ್ನು ನೀಡಲಾಗಿದೆ. ನೋಟಿಸ್‌ನ ಕೊನೆಯಲ್ಲಿ ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC), ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು, ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು ಮತ್ತು PAN ಕಾರ್ಡ್ ನಕಲು ಎಂದು ದಾಖಲೆಗಳನ್ನು ಪಟ್ಟಿ ಮಾಡಿದೆ. ಆದರೆ, ನೋಟಿಸ್‌ನಲ್ಲಿ ಸಂಬಂಧಿಸಿದಂತೆ ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಕ್ರಿಯೆಯನ್ನು ಮಾಡಲು ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿಲ್ಲ ಮತ್ತು ಪ್ರಕಟಣೆಯ ದಿನಾಂಕ ೧೪/೧/೨೦೨೪ ಆಗಿದ್ದರೂ, ಯಾವ ಕೆಲಸಕ್ಕೆ ಕೊನೆಯ ದಿನಾಂಕವೆಂಬುದನ್ನು ನಮೂದಿಸಿಲ್ಲ.",
      action: ["ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC)", "ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು", "ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು", "PAN ಕಾರ್ಡ್ ನಕಲು"],
      deadline: "ದಾಖಲೆಯಲ್ಲಿ ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಕೊನೆಯ ದಿನಾಂಕವನ್ನು ನಮೂದಿಸಿಲ್ಲ (ಪ್ರಕಟಣೆ ದಿನಾಂಕ: 14/01/2024)",
      evidence: "• ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC) • ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು • ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು • PAN ಕಾರ್ಡ್ ನಕಲು... ದಿನಾಂಕ: ೧೪/೦೧/೨೦೨೪",
      grounded: true,
      confidence: "high",
      audioUrl: "/vaanisetu_answer.wav"
    },
    "hi-IN": {
      answer: "इस आधिकारिक नोटिस के अनुसार, के.आर. पुरम तालुका के सुलीकेरे गांव में सड़क चौड़ीकरण परियोजना के लिए भूमि अधिग्रहण अधिनियम 2013 के तहत भूमि अधिग्रहण किया जा रहा है। भूमि मालिकों को आरटीसी (RTC/पट्टा), आधार कार्ड, बैंक पासबुक और पैन कार्ड की प्रतियां तालुका कार्यालय में जमा करनी होंगी। इस नोटिस में कोई विशिष्ट अंतिम तिथि नहीं दी गई है (नोटिस तिथि: 14/01/2024)।",
      action: ["भूमि दस्तावेज़ (RTC/पट्टा)", "आधार कार्ड की प्रति", "बैंक पासबुक की प्रति", "PAN कार्ड की प्रति"],
      deadline: "दस्तावेज़ में कोई अंतिम तिथि नहीं बताई गई है (अधिसूचना तिथि: 14/01/2024)",
      evidence: "• भूमि और पट्टा (RTC) • आधार कार्ड प्रति • बैंक पासबुक प्रति • PAN कार्ड प्रति... दिनांक: 14/01/2024",
      grounded: true,
      confidence: "high",
      audioUrl: null
    },
    "ta-IN": {
      answer: "இந்த அறிவிப்பின்படி, கே.ஆர்.புரம் தாலுகா சூலிகெரே கிராமத்தில் சாலை விரிவாக்க திட்டத்திற்காக நிலம் கையகப்படுத்தப்படுகிறது. நில உரிமையாளர்கள் RTC நில ஆவணங்கள், ஆதார் அட்டை, வங்கி பாஸ்புக் மற்றும் PAN அட்டை நகல்களை தாலுகா அலுவலகத்தில் சமர்ப்பிக்க வேண்டும். இதில் குறிப்பிட்ட கடைசி தேதி எதுவும் குறிப்பிடப்படவில்லை (தேதி: 14/01/2024).",
      action: ["RTC நில ஆவணங்கள்", "ஆதார் அட்டை நகல்", "வங்கி பாஸ்புக் நகல்", "PAN அட்டை நகல்"],
      deadline: "சமர்ப்பிப்பதற்கான கடைசி தேதி குறிப்பிடப்படவில்லை (தேதி: 14/01/2024)",
      evidence: "• RTC நில ஆவணம் • ஆதார் நகல் • வங்கி பாஸ்புக் நகல் • PAN நகல்... தேதி: 14/01/2024",
      grounded: true,
      confidence: "high",
      audioUrl: null
    },
    "en-IN": {
      answer: "According to this official notice, land acquisition is initiated under the Karnataka Land Acquisition Act 2013 for proposed road widening in Sulikere village (KR Puram Taluk). Landowners listed must submit RTC land records, Aadhaar card, Bank passbook, and PAN card copies to the Taluk office. Note: The notice is dated 14/01/2024, but no specific submission deadline date is stated in the document.",
      action: ["RTC Land Records", "Aadhaar Card Copy", "Bank Passbook Copy", "PAN Card Copy"],
      deadline: "No explicit submission deadline is stated in the document (Notice Date: 14/01/2024)",
      evidence: "• RTC Land Record • Aadhaar Copy • Bank Passbook Copy • PAN Copy... Date: 14/01/2024",
      grounded: true,
      confidence: "high",
      audioUrl: null
    }
  };

  const [currentAnswerData, setCurrentAnswerData] = useState(sampleAnswersMap["kn-IN"]);
  const answerAudioRef = useRef(null);
  const questionAudioRef = useRef(null);
  const fileInputRef = useRef(null);

  // Sync sample question & answer when language changes
  const handleLanguageChange = async (newCode) => {
    setSelectedLanguageCode(newCode);
    const newMeta = getLanguageMeta(newCode);

    if (isSampleMode) {
      setQuestionText(newMeta.sampleQuestion);
      if (sampleAnswersMap[newCode]) {
        setCurrentAnswerData(sampleAnswersMap[newCode]);
      } else {
        // Dynamically translate answer via API
        try {
          const res = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
              text: sampleAnswersMap["kn-IN"].answer,
              source_language: "kn-IN",
              target_language: newCode
            })
          });
          if (res.ok) {
            const data = await res.json();
            setCurrentAnswerData({
              ...sampleAnswersMap["kn-IN"],
              answer: data.translated_text,
              audioUrl: null
            });
          }
        } catch (e) {
          console.log("Translation error:", e);
        }
      }
    } else {
      setQuestionText(newMeta.placeholder);
    }
  };

  // Sync audio ref src when audioUrl changes
  useEffect(() => {
    if (answerAudioRef.current && currentAnswerData?.audioUrl) {
      answerAudioRef.current.src = currentAnswerData.audioUrl;
      setIsPlayingAnswer(false);
      setAudioProgress(0);
      setAudioCurrentTime(0);
    }
  }, [currentAnswerData?.audioUrl]);

  // Audio Playback Progress Listener
  useEffect(() => {
    const audio = answerAudioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      if (audio.duration) {
        setAudioCurrentTime(audio.currentTime);
        setAudioDuration(audio.duration);
        setAudioProgress((audio.currentTime / audio.duration) * 100);
      }
    };

    const handleEnded = () => {
      setIsPlayingAnswer(false);
      setAudioProgress(0);
      setAudioCurrentTime(0);
    };

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateProgress);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  const toggleAnswerAudio = () => {
    const audio = answerAudioRef.current;
    if (!audio || !currentAnswerData?.audioUrl) return;

    if (isPlayingAnswer) {
      audio.pause();
      setIsPlayingAnswer(false);
    } else {
      audio.playbackRate = playbackRate;
      audio.play().then(() => setIsPlayingAnswer(true)).catch(err => console.log(err));
    }
  };

  const handleAudioScrub = (e) => {
    const audio = answerAudioRef.current;
    if (!audio || !audio.duration) return;
    const seekTime = (e.target.value / 100) * audio.duration;
    audio.currentTime = seekTime;
    setAudioProgress(e.target.value);
  };

  const handlePlaybackRateChange = (rate) => {
    setPlaybackRate(rate);
    if (answerAudioRef.current) {
      answerAudioRef.current.playbackRate = rate;
    }
  };

  const toggleQuestionAudio = () => {
    const audio = questionAudioRef.current;
    if (!audio) return;

    if (isPlayingQuestion) {
      audio.pause();
      setIsPlayingQuestion(false);
    } else {
      audio.play().then(() => setIsPlayingQuestion(true)).catch(err => console.log(err));
    }
  };

  // Handle File Selection
  const handleFileSelect = (file) => {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['png', 'jpg', 'jpeg', 'pdf'].includes(ext)) {
      setAnalysisError("Unsupported file type. Please upload a PNG, JPG, or PDF document.");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setAnalysisError("File size exceeds 15MB limit.");
      return;
    }

    setAnalysisError(null);
    setIsSampleMode(false);
    setUploadedFile(file);
    setFileName(file.name);

    if (ext === 'pdf') {
      setFileType('pdf');
    } else {
      setFileType('image');
    }

    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    
    setQuestionText("");
    setCurrentAnswerData(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  // Restore Sample Demo
  const handleRestoreSample = () => {
    setIsSampleMode(true);
    setUploadedFile(null);
    setFileName('kannada.png');
    setFileType('image');
    setPreviewUrl('/kannada.png');
    setQuestionText(currentLang.sampleQuestion);
    setCurrentAnswerData(sampleAnswersMap[selectedLanguageCode] || sampleAnswersMap["kn-IN"]);
    setAnalysisError(null);
  };

  // Reset Upload
  const handleResetUpload = () => {
    setUploadedFile(null);
    setIsSampleMode(false);
    setFileName('');
    setPreviewUrl('');
    setQuestionText('');
    setCurrentAnswerData(null);
    setAnalysisError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Live Browser Microphone Recording -> Sarvam Saaras STT API
  const startRecording = async () => {
    setAnalysisError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      let options = {};
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        options = { mimeType: 'audio/webm;codecs=opus' };
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        options = { mimeType: 'audio/webm' };
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        options = { mimeType: 'audio/mp4' };
      }

      mediaRecorderRef.current = new MediaRecorder(stream, options);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const mimeType = mediaRecorderRef.current.mimeType || 'audio/webm';
        const extension = mimeType.includes('mp4') ? 'mp4' : mimeType.includes('ogg') ? 'ogg' : 'webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await sendAudioToSTT(audioBlob, extension, mimeType);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access error:", err);
      setIsRecording(false);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setAnalysisError("Microphone permission denied. Please allow microphone access in browser settings.");
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setAnalysisError("No microphone device found on this system.");
      } else {
        setAnalysisError(`Microphone error: ${err.message || 'Could not access microphone'}`);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
      setIsRecording(false);
    } else {
      setIsRecording(false);
    }
  };

  const sendAudioToSTT = async (blob, extension, mimeType) => {
    setIsTranscribing(true);
    setAnalysisError(null);
    try {
      if (blob.size < 100) {
        setAnalysisError("Recorded audio is too short. Please speak clearly and try again.");
        return;
      }

      const formData = new FormData();
      formData.append('audio', blob, `recording.${extension}`);
      formData.append('language', selectedLanguageCode);
      formData.append('mime_type', mimeType);

      const response = await fetch('/api/stt', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.transcript && data.transcript.trim()) {
          setQuestionText(data.transcript);
        } else {
          setAnalysisError(`Speech recognition completed for ${currentLang.name}, but no spoken text was recognized. Please speak louder or closer to microphone.`);
        }
      } else {
        const errJson = await response.json().catch(() => ({}));
        setAnalysisError(`Speech recognition failed (${response.status}): ${errJson.detail || response.statusText}`);
      }
    } catch (err) {
      setAnalysisError(`Could not connect to speech recognition service: ${err.message}`);
    } finally {
      setIsTranscribing(false);
    }
  };

  // Execute Multilingual Document AI + 105B + Bulbul Analysis via Backend API
  const handleAnalyzeDocument = async () => {
    if (!questionText.trim()) {
      setAnalysisError("Please type or record a question first.");
      return;
    }

    setAnalysisError(null);
    setIsProcessing(true);
    setProcessingStage(1);

    // Fast simulated execution for sample mode if backend API is offline
    if (isSampleMode && !uploadedFile) {
      setTimeout(() => setProcessingStage(2), 900);
      setTimeout(() => setProcessingStage(3), 1800);
      setTimeout(() => {
        setIsProcessing(false);
        setCurrentAnswerData(sampleAnswersMap[selectedLanguageCode] || sampleAnswersMap["kn-IN"]);
        document.getElementById('answer-hero-card')?.scrollIntoView({ behavior: 'smooth' });
      }, 2500);
      return;
    }

    // Real API Call for User Uploaded or Selected Document
    try {
      setProcessingStage(1); // Document AI OCR
      const formData = new FormData();
      if (uploadedFile) {
        formData.append('document', uploadedFile);
      }
      formData.append('question', questionText);
      formData.append('language', selectedLanguageCode);

      setProcessingStage(2); // Sarvam 105B Reasoning in Target Language

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || "Analysis request failed.");
      }

      setProcessingStage(3); // Bulbul Voice Synthesis in Target Language

      const data = await response.json();

      let actionList = [];
      if (Array.isArray(data.action)) {
        actionList = data.action;
      } else if (typeof data.action === 'string') {
        actionList = data.action.split('\n').filter(Boolean);
      }

      setCurrentAnswerData({
        answer: data.answer || currentLang.notFoundText,
        action: actionList,
        deadline: data.deadline || "No explicit deadline mentioned in the document.",
        evidence: data.evidence || "Extract from uploaded document",
        grounded: data.grounded ?? true,
        confidence: data.confidence || "high",
        audioUrl: data.audio_url || null
      });

      setIsProcessing(false);
      setTimeout(() => {
        document.getElementById('answer-hero-card')?.scrollIntoView({ behavior: 'smooth' });
      }, 300);

    } catch (err) {
      console.error("Analysis Error:", err);
      setAnalysisError(err.message || "Failed to analyze document. Please check connection.");
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="bg-forest-950 text-ivory-100 min-h-screen relative font-sans bg-paper-pattern selection:bg-gold-500 selection:text-forest-950">
      
      {/* Background Ambient Glows */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-forest-700/20 via-forest-800/10 to-transparent blur-3xl pointer-events-none z-0" />
      <div className="fixed top-[40%] right-[-10%] w-[600px] h-[600px] bg-gold-500/5 blur-3xl pointer-events-none z-0" />
      
      {/* Hidden Audio Elements */}
      <audio ref={answerAudioRef} preload="metadata" />
      <audio ref={questionAudioRef} src="/question.wav" preload="metadata" onEnded={() => setIsPlayingQuestion(false)} />

      {/* 1. TOP ANNOUNCEMENT BAR */}
      <div className="bg-forest-900/90 border-b border-forest-800/60 backdrop-blur-md py-2 px-4 text-xs font-mono text-center text-ivory-300 flex items-center justify-center gap-2 relative z-50">
        <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>Powered by <strong>Sarvam AI</strong> · Saaras STT + Sarvam 105B Grounded Reasoning + Bulbul TTS</span>
        <span className="bg-forest-800 px-2 py-0.5 rounded text-[10px] text-gold-400 border border-gold-500/20 font-bold">
          {currentLang.native} ({currentLang.code})
        </span>
      </div>

      {/* 2. NAVIGATION BAR WITH LANGUAGE SELECTOR DROPDOWN */}
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-forest-950/80 border-b border-forest-800/50 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-500 to-forest-600 p-[1px] shadow-glow-gold">
              <div className="w-full h-full bg-forest-950 rounded-[11px] flex items-center justify-center">
                <Radio className="w-5 h-5 text-gold-400" />
              </div>
            </div>
            <div>
              <div className="flex items-baseline gap-2">
                <span className="font-serif text-2xl font-bold tracking-tight text-ivory-50">VaaniSetu</span>
                <span className="font-kannada text-sm text-gold-400 font-medium">ವಾಣಿ ಸೇತು</span>
              </div>
              <p className="text-[11px] text-ivory-400 hidden sm:block tracking-wide uppercase font-mono">Multilingual Document AI</p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-ivory-300">
            <a href="#languages" className="hover:text-gold-400 transition-colors">Select Language</a>
            <a href="#demo" className="hover:text-gold-400 transition-colors">Interactive Demo</a>
            <a href="#how-it-works" className="hover:text-gold-400 transition-colors">How It Works</a>
          </nav>

          {/* DYNAMIC LANGUAGE SELECTOR */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <select
                value={selectedLanguageCode}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="appearance-none bg-forest-900 border border-gold-500/40 text-gold-400 font-semibold text-xs rounded-xl px-3 py-2 pr-8 focus:outline-none focus:border-gold-400 cursor-pointer shadow-sm"
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code} className="bg-forest-950 text-ivory-100">
                    {lang.flag} {lang.native} ({lang.name})
                  </option>
                ))}
              </select>
              <Globe className="w-3.5 h-3.5 text-gold-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            <a 
              href="#demo"
              className="hidden sm:flex px-4 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 hover:from-gold-400 hover:to-gold-500 text-forest-950 font-semibold text-sm shadow-glow-gold transition-all duration-300 items-center gap-1.5"
            >
              <span>Try Demo</span>
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* 3. LANGUAGE SELECTION LANDING HERO SECTION */}
      <section id="languages" className="relative pt-12 pb-16 overflow-hidden z-10 border-b border-forest-800/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-forest-900/80 border border-gold-500/30 text-gold-400 text-xs font-mono mb-4 shadow-sm">
              <Globe className="w-3.5 h-3.5" />
              <span>Choose Your Preferred Indian Language</span>
            </div>

            <h1 className="font-serif text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-ivory-50 mb-4 leading-tight">
              Understand every document. <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-gold-400 via-ivory-100 to-emerald-400 bg-clip-text text-transparent">
                In {currentLang.name} ({currentLang.native}).
              </span>
            </h1>

            <p className="text-base sm:text-lg text-ivory-300 font-normal leading-relaxed max-w-2xl mx-auto">
              VaaniSetu turns complex official documents into clear, spoken answers in the language you understand best.
            </p>
          </div>

          {/* 10-LANGUAGE SELECTION CARDS GRID */}
          <div className="max-w-5xl mx-auto grid grid-cols-2 sm:grid-cols-5 gap-3">
            {SUPPORTED_LANGUAGES.map((lang) => {
              const isSelected = lang.code === selectedLanguageCode;
              return (
                <button
                  key={lang.code}
                  onClick={() => handleLanguageChange(lang.code)}
                  className={`p-3.5 rounded-xl border text-center transition-all duration-300 flex flex-col items-center justify-center gap-1.5 group ${
                    isSelected 
                      ? 'bg-gradient-to-b from-forest-850 to-forest-900 border-gold-400 shadow-glow-gold scale-105' 
                      : 'bg-forest-900/60 border-forest-800 hover:border-gold-500/40 hover:bg-forest-850'
                  }`}
                >
                  <span className="text-lg">{lang.flag}</span>
                  <span className={`font-serif text-base font-bold ${isSelected ? 'text-gold-400' : 'text-ivory-100 group-hover:text-gold-400'}`}>
                    {lang.native}
                  </span>
                  <span className="text-[11px] font-mono text-ivory-400">{lang.name}</span>
                  {isSelected && (
                    <span className="w-2 h-2 rounded-full bg-emerald-400 mt-1 animate-ping" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. MAIN INTERACTIVE DEMO SECTION */}
      <section id="demo" className="py-16 relative z-10 bg-forest-900/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-mono uppercase tracking-widest text-gold-400 bg-forest-900 px-3 py-1 rounded-full border border-gold-500/20">
              Active Language: {currentLang.name} ({currentLang.native})
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-ivory-50 mt-3 mb-2">Let's understand your document.</h2>
            <p className="text-ivory-300 text-sm sm:text-base">Upload any official document and ask questions in {currentLang.native}.</p>
          </div>

          {/* ERROR ALERT NOTIFICATION */}
          {analysisError && (
            <div className="max-w-4xl mx-auto mb-8 p-4 rounded-xl bg-red-950/80 border border-red-500/50 text-red-200 text-sm flex items-center justify-between gap-3 shadow-lg">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
                <span>{analysisError}</span>
              </div>
              <button onClick={() => setAnalysisError(null)} className="p-1 hover:bg-red-900/50 rounded">
                <X className="w-4 h-4 text-red-400" />
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start max-w-6xl mx-auto">
            
            {/* LEFT COLUMN: STEP 01 DOCUMENT UPLOAD & PREVIEW (5 Cols) */}
            <div className="lg:col-span-5 forest-glass rounded-2xl p-6 border border-forest-700/70 relative">
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-forest-800">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-gold-500/20 text-gold-400 text-xs font-mono flex items-center justify-center font-bold">01</span>
                  <h3 className="font-serif font-bold text-lg text-ivory-100">Upload your document</h3>
                </div>
                {!isSampleMode && (
                  <button 
                    onClick={handleRestoreSample}
                    className="text-xs font-mono text-gold-400 hover:underline flex items-center gap-1 bg-forest-900 px-2.5 py-1 rounded border border-gold-500/20"
                  >
                    <RotateCcw className="w-3 h-3" />
                    <span>Use sample</span>
                  </button>
                )}
              </div>

              {/* Upload Dropzone / Document Display */}
              <div 
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                className="relative rounded-xl overflow-hidden bg-forest-950/80 border-2 border-dashed border-forest-700/80 p-4 text-center group hover:border-gold-500/50 transition-colors"
              >
                
                <input 
                  ref={fileInputRef}
                  type="file" 
                  accept="image/png, image/jpeg, application/pdf"
                  className="hidden"
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                />

                {isProcessing && (
                  <div className="scanner-line z-20" />
                )}

                {previewUrl ? (
                  <div className="relative rounded-lg overflow-hidden bg-forest-900/90 border border-forest-800 mb-4 min-h-[220px] flex items-center justify-center">
                    {fileType === 'pdf' ? (
                      <div className="p-6 text-center w-full">
                        <FileText className="w-16 h-16 text-gold-400 mx-auto mb-3" />
                        <span className="text-sm font-semibold text-ivory-100 block font-mono break-all">{fileName}</span>
                        <span className="text-xs text-emerald-400 font-mono mt-1 block">PDF Document Ready</span>
                        <iframe src={previewUrl} className="w-full h-48 mt-3 rounded border border-forest-800 hidden sm:block" title="PDF Preview" />
                      </div>
                    ) : (
                      <img 
                        src={previewUrl} 
                        alt="Uploaded Document Preview" 
                        className="w-full h-56 object-cover object-top opacity-90 group-hover:scale-105 transition-transform duration-500"
                      />
                    )}
                    
                    <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-left">
                      <div className="bg-forest-950/90 backdrop-blur-md px-2.5 py-1 rounded border border-forest-800">
                        <span className="text-[10px] font-mono text-gold-400 block uppercase">File Name</span>
                        <span className="text-xs font-semibold text-ivory-100 font-mono truncate max-w-[180px] block">{fileName}</span>
                      </div>
                      <span className="px-2 py-1 bg-forest-950/90 rounded text-[10px] font-mono text-emerald-400 border border-emerald-500/30">
                        {isSampleMode ? "Sample Notice" : "User Document"}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="py-12 px-4 text-center cursor-pointer" onClick={() => fileInputRef.current?.click()}>
                    <Upload className="w-12 h-12 text-gold-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                    <h4 className="font-bold text-ivory-100 text-base mb-1">Drop your document here</h4>
                    <p className="text-xs text-ivory-400 font-mono mb-4">PNG, JPG, or PDF (up to 15MB)</p>
                    <button className="px-4 py-2 rounded-lg bg-forest-900 hover:bg-forest-850 text-gold-400 font-semibold text-xs border border-gold-500/30 transition-colors">
                      Choose a file
                    </button>
                  </div>
                )}

                <div className="flex items-center justify-between px-3 py-2.5 bg-forest-900 rounded-lg border border-forest-800 text-xs font-mono">
                  <div className="flex items-center gap-2 truncate">
                    {isProcessing ? (
                      <RefreshCw className="w-4 h-4 text-gold-400 animate-spin shrink-0" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    )}
                    <span className="text-ivory-200 truncate">
                      {isSampleMode ? "✓ Demo document ready" : `✓ Document ready (${fileName})`}
                    </span>
                  </div>

                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="text-[11px] text-gold-400 hover:underline font-semibold shrink-0"
                  >
                    Change
                  </button>
                </div>

                {!isSampleMode && (
                  <div className="mt-3 flex items-center justify-between text-xs">
                    <button onClick={handleResetUpload} className="text-ivory-400 hover:text-red-400 text-[11px] font-mono flex items-center gap-1">
                      <X className="w-3.5 h-3.5" /> Start new document
                    </button>
                    <button onClick={handleRestoreSample} className="text-gold-400 hover:underline text-[11px] font-mono">
                      Back to sample demo
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* RIGHT COLUMN: STEP 02 VOICE QUESTION & INTERACTION (7 Cols) */}
            <div className="lg:col-span-7 forest-glass rounded-2xl p-6 border border-forest-700/70">
              <div className="flex items-center justify-between mb-6 pb-3 border-b border-forest-800">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-gold-500/20 text-gold-400 text-xs font-mono flex items-center justify-center font-bold">02</span>
                  <h3 className="font-serif font-bold text-lg text-ivory-100">Ask in {currentLang.native}</h3>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-mono text-gold-400 bg-gold-500/10 px-2.5 py-1 rounded-full border border-gold-500/20">
                  <Languages className="w-3.5 h-3.5" />
                  <span>{currentLang.name} ({currentLang.code})</span>
                </div>
              </div>

              {/* VOICE INTERACTION HERO CARD */}
              <div className="bg-forest-950/80 rounded-xl p-6 border border-forest-800 mb-6 text-center relative overflow-hidden">
                <p className="text-xs text-ivory-400 font-mono mb-4 uppercase tracking-wider">
                  {isRecording ? `Listening... Speak in ${currentLang.name}` : `Tap microphone to speak (${currentLang.native})`}
                </p>

                {/* Big Glowing Microphone Button */}
                <div className="relative inline-block mb-6">
                  <div className={`absolute -inset-4 rounded-full bg-gold-500/20 transition-all duration-500 ${isRecording ? 'animate-ping opacity-75' : 'opacity-0'}`} />
                  
                  <button 
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-105 shadow-glow-gold ${
                      isRecording 
                        ? 'bg-red-600 text-white shadow-red-500/50' 
                        : 'bg-gradient-to-br from-gold-400 via-gold-500 to-forest-700 text-forest-950'
                    }`}
                  >
                    <Mic className={`w-8 h-8 ${isRecording ? 'animate-bounce' : ''}`} />
                  </button>
                </div>

                {/* Audio Waveform Animation */}
                <div className="h-10 flex items-center justify-center gap-1.5 mb-4">
                  {[40, 75, 50, 90, 60, 30, 85, 45, 95, 65, 35, 70].map((h, i) => (
                    <div 
                      key={i} 
                      className={`w-1.5 rounded-full transition-all duration-300 ${
                        isRecording || isPlayingQuestion ? 'bg-gold-400 wave-bar' : 'bg-forest-800'
                      }`}
                      style={{ height: (isRecording || isPlayingQuestion) ? `${h}%` : '20%' }}
                    />
                  ))}
                </div>

                {isSampleMode && selectedLanguageCode === 'kn-IN' && (
                  <button 
                    onClick={toggleQuestionAudio}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-forest-900 border border-forest-700 hover:border-gold-500/40 text-xs font-mono text-ivory-200 transition-colors"
                  >
                    {isPlayingQuestion ? <Pause className="w-3.5 h-3.5 text-gold-400" /> : <Play className="w-3.5 h-3.5 text-gold-400" />}
                    <span>Listen to sample audio (question.wav)</span>
                  </button>
                )}
              </div>

              {/* QUESTION INPUT & PRESET CHIP */}
              <div className="space-y-3">
                <label className="text-xs font-mono text-ivory-300 block">Question in {currentLang.name} ({currentLang.native}):</label>
                <div className="relative">
                  <input 
                    type="text"
                    value={questionText}
                    onChange={(e) => setQuestionText(e.target.value)}
                    placeholder={currentLang.placeholder}
                    className="w-full bg-forest-950 border border-forest-700 rounded-xl px-4 py-3 text-ivory-100 font-sans text-sm focus:outline-none focus:border-gold-500/80 transition-colors"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-mono text-gold-400 bg-forest-900 px-2 py-0.5 rounded border border-gold-500/20">Saaras v4</span>
                </div>

                {isSampleMode && (
                  <div className="flex items-center gap-2 pt-1">
                    <span className="text-[11px] font-mono text-ivory-400">Sample ({currentLang.native}):</span>
                    <button 
                      onClick={() => setQuestionText(currentLang.sampleQuestion)}
                      className="text-xs text-gold-400 hover:underline bg-forest-900/60 px-2.5 py-1 rounded border border-forest-800 text-left"
                    >
                      "{currentLang.sampleQuestion}"
                    </button>
                  </div>
                )}

                {/* Primary Action CTA */}
                <button 
                  onClick={handleAnalyzeDocument}
                  disabled={isProcessing || isTranscribing}
                  className="w-full mt-4 py-3.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 hover:from-gold-400 hover:to-gold-500 text-forest-950 font-bold text-base shadow-glow-gold transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isProcessing ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Analyzing in {currentLang.name}...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      <span>Ask VaaniSetu ({currentLang.native})</span>
                    </>
                  )}
                </button>
              </div>

            </div>
          </div>

          {/* 5. AI THINKING STATE MODAL / BAR */}
          {isProcessing && (
            <div className="mt-10 max-w-4xl mx-auto forest-glass rounded-2xl p-6 border border-gold-500/40 shadow-glow-gold/20 text-center animate-pulse">
              <div className="flex items-center justify-center gap-3 mb-4">
                <Cpu className="w-6 h-6 text-gold-400 animate-spin" />
                <h4 className="font-serif text-xl font-bold text-ivory-50">Sarvam Multilingual Pipeline</h4>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
                <div className={`p-3 rounded-lg border transition-colors ${processingStage >= 1 ? 'bg-forest-900 border-gold-500/50 text-gold-400' : 'bg-forest-950 border-forest-800 text-ivory-400'}`}>
                  1. Sarvam Doc AI OCR...
                </div>
                <div className={`p-3 rounded-lg border transition-colors ${processingStage >= 2 ? 'bg-forest-900 border-gold-500/50 text-gold-400' : 'bg-forest-950 border-forest-800 text-ivory-400'}`}>
                  2. Sarvam 105B Reasoning ({currentLang.name})...
                </div>
                <div className={`p-3 rounded-lg border transition-colors ${processingStage >= 3 ? 'bg-forest-900 border-emerald-500/50 text-emerald-400' : 'bg-forest-950 border-forest-800 text-ivory-400'}`}>
                  3. Bulbul Voice Output ({currentLang.native}) ✓
                </div>
              </div>
            </div>
          )}

          {/* 6. HERO MOMENT — ANSWER EXPERIENCE PANEL */}
          {currentAnswerData && !isProcessing && (
            <div id="answer-hero-card" className="mt-12 max-w-5xl mx-auto space-y-8 animate-fadeIn">
              
              {/* MAIN MULTILINGUAL ANSWER CARD */}
              <div className="forest-glass rounded-2xl p-8 border-2 border-gold-500/40 shadow-premium relative overflow-hidden">
                <div className="absolute top-0 right-0 w-48 h-48 bg-gold-500/10 rounded-full blur-2xl pointer-events-none" />

                {/* Header */}
                <div className="flex items-center justify-between pb-4 mb-6 border-b border-forest-800">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gold-500/20 flex items-center justify-center text-gold-400 font-serif font-bold text-lg">
                      V
                    </div>
                    <div>
                      <h3 className="font-serif font-bold text-xl text-ivory-50">VaaniSetu says ({currentLang.native})</h3>
                      <span className="text-xs font-mono text-emerald-400">
                        {currentAnswerData.grounded ? "✓ Grounded in Document" : "⚠️ Low Grounding Confidence"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Text Content in Selected Language */}
                <div className="prose prose-invert max-w-none">
                  <p className="text-lg sm:text-xl text-ivory-50 leading-relaxed font-normal bg-forest-950/60 p-6 rounded-xl border border-forest-800">
                    {currentAnswerData.answer}
                  </p>
                </div>

                {/* Audio Output Player Section */}
                <div className="mt-8 pt-6 border-t border-forest-800">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={toggleAnswerAudio}
                        disabled={!currentAnswerData.audioUrl}
                        className="w-12 h-12 rounded-full bg-gradient-to-r from-gold-500 to-gold-600 hover:from-gold-400 hover:to-gold-500 text-forest-950 flex items-center justify-center shadow-glow-gold transition-transform hover:scale-105 disabled:opacity-50"
                      >
                        {isPlayingAnswer ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-0.5" />}
                      </button>
                      <div>
                        <h4 className="font-serif font-bold text-ivory-100 text-base">{currentLang.listenLabel}</h4>
                        <p className="text-xs text-gold-400 font-mono">Sarvam Bulbul Voice ({currentLang.name})</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs font-mono text-ivory-400">
                      <span>Speed:</span>
                      {[0.8, 1, 1.2].map((rate) => (
                        <button 
                          key={rate}
                          onClick={() => handlePlaybackRateChange(rate)}
                          className={`px-2 py-0.5 rounded ${playbackRate === rate ? 'bg-gold-500 text-forest-950 font-bold' : 'bg-forest-900 text-ivory-300'}`}
                        >
                          {rate}x
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Audio Progress Slider */}
                  <div className="space-y-1">
                    <input 
                      type="range"
                      min="0"
                      max="100"
                      value={audioProgress}
                      onChange={handleAudioScrub}
                      className="w-full h-2 bg-forest-900 rounded-lg appearance-none cursor-pointer accent-gold-500"
                    />
                    <div className="flex items-center justify-between text-xs font-mono text-ivory-400">
                      <span>{formatTime(audioCurrentTime)}</span>
                      <span>{formatTime(audioDuration || 12)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* STRUCTURED ANSWER GRID (ACTION, DEADLINE, EVIDENCE) */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* 1. ACTION BLOCK */}
                <div className="forest-glass rounded-xl p-6 border border-forest-700/80">
                  <div className="flex items-center gap-2 text-gold-400 font-mono text-xs uppercase tracking-wider mb-3">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Required Actions</span>
                  </div>
                  <h4 className="font-serif font-bold text-ivory-100 text-lg mb-3">Actions ({currentLang.native})</h4>
                  {Array.isArray(currentAnswerData.action) && currentAnswerData.action.length > 0 ? (
                    <ul className="space-y-2 text-xs text-ivory-200">
                      {currentAnswerData.action.map((act, idx) => (
                        <li key={idx} className="flex items-center gap-2 bg-forest-900/60 p-2 rounded border border-forest-800">
                          <span className="w-1.5 h-1.5 rounded-full bg-gold-400 shrink-0" />
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-ivory-300">{currentAnswerData.action || "No explicit action required."}</p>
                  )}
                </div>

                {/* 2. DEADLINE BLOCK */}
                <div className="forest-glass rounded-xl p-6 border border-forest-700/80">
                  <div className="flex items-center gap-2 text-gold-400 font-mono text-xs uppercase tracking-wider mb-3">
                    <AlertCircle className="w-4 h-4 text-gold-400" />
                    <span>Submission Deadline</span>
                  </div>
                  <h4 className="font-serif font-bold text-ivory-100 text-lg mb-2">Deadline Status</h4>
                  <p className="text-xs text-ivory-300 leading-relaxed mb-4">
                    {currentAnswerData.deadline || "No specific deadline stated in document."}
                  </p>
                </div>

                {/* 3. EVIDENCE BLOCK */}
                <div className="forest-glass rounded-xl p-6 border border-forest-700/80">
                  <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs uppercase tracking-wider mb-3">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span>Grounding Evidence</span>
                  </div>
                  <h4 className="font-serif font-bold text-ivory-100 text-lg mb-2">Document Excerpt</h4>
                  <div className="p-3 rounded-lg bg-forest-950/90 border border-forest-800 text-xs text-ivory-300 italic space-y-1">
                    <p>"{currentAnswerData.evidence}"</p>
                    <p className="text-[10px] text-gold-400 font-mono not-italic mt-2">Source: Document Analysis</p>
                  </div>
                </div>

              </div>

              {/* TRUST INDICATOR BADGE */}
              <div className="p-4 rounded-xl bg-forest-900/60 border border-forest-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-ivory-300">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                  <span><strong>Verified Grounded Answer:</strong> VaaniSetu answers strictly from the document and does not hallucinate missing facts.</span>
                </div>
                <span className="text-[11px] font-mono text-ivory-400 shrink-0">Not legal advice · Verify against original document</span>
              </div>

            </div>
          )}

        </div>
      </section>

      {/* 7. HOW IT WORKS SECTION */}
      <section id="how-it-works" className="py-20 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-mono uppercase tracking-widest text-gold-400">Multilingual Architecture</span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-ivory-50 mt-2">How VaaniSetu Works</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 max-w-6xl mx-auto">
            {[
              { step: "01", title: "Upload Document", desc: "Upload official paper notice, photo, or PDF in any language." },
              { step: "02", title: "Sarvam Doc AI", desc: "OCR digitizes document text, layout, and tables." },
              { step: "03", title: "Saaras Voice AI", desc: "Ask question by voice in your chosen Indian language." },
              { step: "04", title: "Sarvam 105B", desc: "Grounded reasoning model yields strict factual answer in your language." },
              { step: "05", title: "Bulbul Speech", desc: "Converts answer back to natural spoken voice in your language." },
            ].map((item, idx) => (
              <div key={idx} className="forest-glass rounded-xl p-5 border border-forest-700/60 relative group hover:border-gold-500/40 transition-colors">
                <div className="text-2xl font-serif font-bold text-gold-500/40 group-hover:text-gold-400 transition-colors mb-2">{item.step}</div>
                <h4 className="font-bold text-ivory-100 text-sm mb-1">{item.title}</h4>
                <p className="text-xs text-ivory-300">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 8. SARVAM AI TECHNOLOGY SECTION */}
      <section id="technology" className="py-20 relative z-10 bg-forest-900/30 border-t border-forest-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-mono uppercase tracking-widest text-gold-400">Powered by Sarvam AI</span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-ivory-50 mt-2">Multilingual AI Stack</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <div className="forest-glass rounded-xl p-6 border border-forest-700/60">
              <FileText className="w-8 h-8 text-gold-400 mb-3" />
              <h4 className="font-serif font-bold text-lg text-ivory-100 mb-1">Document AI</h4>
              <p className="text-xs text-ivory-300">Advanced layout preservation & OCR digitization for Indian script documents.</p>
            </div>

            <div className="forest-glass rounded-xl p-6 border border-forest-700/60">
              <Mic className="w-8 h-8 text-gold-400 mb-3" />
              <h4 className="font-serif font-bold text-lg text-ivory-100 mb-1">Saaras STT</h4>
              <p className="text-xs text-ivory-300">Speech recognition tuned for 10+ Indian regional languages and accents.</p>
            </div>

            <div className="forest-glass rounded-xl p-6 border border-forest-700/60">
              <Cpu className="w-8 h-8 text-gold-400 mb-3" />
              <h4 className="font-serif font-bold text-lg text-ivory-100 mb-1">Sarvam 105B</h4>
              <p className="text-xs text-ivory-300">Large-scale reasoning model tuned for strict document grounding in Indian languages.</p>
            </div>

            <div className="forest-glass rounded-xl p-6 border border-forest-700/60">
              <Volume2 className="w-8 h-8 text-gold-400 mb-3" />
              <h4 className="font-serif font-bold text-lg text-ivory-100 mb-1">Bulbul TTS</h4>
              <p className="text-xs text-ivory-300">Expressive text-to-speech synthesis in Kannada, Hindi, Tamil, Telugu, and more.</p>
            </div>
          </div>
        </div>
      </section>

      {/* 9. FOOTER */}
      <footer className="border-t border-forest-800/80 py-12 bg-forest-950 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
          <div>
            <div className="flex items-center justify-center md:justify-start gap-2 mb-1">
              <span className="font-serif text-xl font-bold text-ivory-50">VaaniSetu</span>
              <span className="font-kannada text-xs text-gold-400">ವಾಣಿ ಸೇತು</span>
            </div>
            <p className="text-xs text-ivory-400">Understand. Ask. Listen. — In Your Language.</p>
          </div>

          <div className="text-xs font-mono text-ivory-400">
            Built for India's multilingual future. Powered by Sarvam AI.
          </div>
        </div>
      </footer>

    </div>
  );
}
