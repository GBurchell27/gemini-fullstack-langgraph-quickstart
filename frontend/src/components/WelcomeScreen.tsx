import { InputForm } from "./InputForm";
import React, { useCallback, useEffect, useState } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Container, Engine, ISourceOptions } from "@tsparticles/engine";

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
  const [init, setInit] = useState(false);

  // This should be run only once per application lifetime
  useEffect(() => {
    initParticlesEngine(async (engine: Engine) => {
      console.log("Loading particles engine...");
      await loadSlim(engine);
      console.log("Particles engine loaded successfully!");
    }).then(() => {
      setInit(true);
    });
  }, []);

  const particlesLoaded = useCallback(async (container?: Container) => {
    console.log("Particles container loaded:", container);
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
        opacity: 0.8,
        width: 2,
      },
      move: {
        direction: "none",
        enable: true,
        outModes: {
          default: "bounce",
        },
        random: false,
        speed: 3,
        straight: false,
      },
      number: {
        density: {
          enable: true,
        },
        value: 50,
      },
      opacity: {
        value: 0.8,
      },
      shape: {
        type: "circle",
      },
      size: {
        value: { min: 3, max: 8 },
      },
    },
    detectRetina: true,
  };

  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-4 flex-1 w-full relative">
      {init && (
        <Particles
          id="tsparticles"
          particlesLoaded={particlesLoaded}
          options={particlesOptions}
          className="absolute top-0 left-0 w-full h-full"
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1 }}
        />
      )}
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
