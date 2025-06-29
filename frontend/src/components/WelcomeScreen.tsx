import { InputForm } from "./InputForm";
import React, { useCallback } from "react";
import Particles from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Engine, ISourceOptions } from "@tsparticles/engine";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => {
  const particlesInit = useCallback(async (engine: Engine) => {
    await loadSlim(engine);
  }, []);

  const particlesOptions: ISourceOptions = {
    background: {
      color: {
        value: "transparent",
      },
    },
    fpsLimit: 60,
    interactivity: {
      events: {
        onClick: {
          enable: true,
          mode: "push",
        },
        onHover: {
          enable: true,
          mode: "repulse",
        },
      },
      modes: {
        push: {
          quantity: 4,
        },
        repulse: {
          distance: 150,
          duration: 0.4,
        },
      },
    },
    particles: {
      color: {
        value: "#ffffff",
      },
      links: {
        color: "#ffffff",
        distance: 150,
        enable: true,
        opacity: 0.2,
        width: 1,
      },
      move: {
        direction: "none",
        enable: true,
        outModes: {
          default: "bounce",
        },
        random: false,
        speed: 2,
        straight: false,
      },
      number: {
        density: {
          enable: true,
        },
        value: 80,
      },
      opacity: {
        value: 0.2,
      },
      shape: {
        type: "circle",
      },
      size: {
        value: { min: 1, max: 5 },
      },
    },
    detectRetina: true,
  };

  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-4 flex-1 w-full relative">
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={particlesOptions}
        className="absolute top-0 left-0 w-full h-full"
      />
      <div className="z-10 flex flex-col items-center justify-center gap-4">
        <div className="animate-fadeInUp">
          <h1 className="text-6xl md:text-8xl font-bold text-white/90 mb-3 tracking-wider">
            A G E N T
          </h1>
          <p className="text-xl md:text-2xl text-white/60">
            Research Assistant Initializing...
          </p>
        </div>
        <div className="w-full mt-8 animate-fadeInUp animation-delay-400">
          <InputForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            onCancel={onCancel}
            hasHistory={false}
          />
        </div>
        <p className="text-xs text-white/40 mt-4 animate-fadeInUp animation-delay-600">
          Powered by Google Gemini and LangChain LangGraph.
        </p>
      </div>
    </div>
  );
};
