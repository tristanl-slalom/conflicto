import { createFileRoute, Link } from '@tanstack/react-router'

import {
  Settings,
  Monitor,
  Smartphone,
  Users,
  BarChart3,
  Zap,
} from 'lucide-react'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  const personas = [
    {
      id: 'admin',
      icon: <Settings className="w-16 h-16 text-blue-400" />,
      title: 'Admin Interface',
      description: 'Configure sessions, manage content, and control activities',
      link: '/admin',
      features: ['Session Management', 'Content Configuration', 'Analytics Dashboard'],
    },
    {
      id: 'viewer',
      icon: <Monitor className="w-16 h-16 text-green-400" />,
      title: 'Viewer Display',
      description: 'Large screen display with QR codes and live results',
      link: '/viewer',
      features: ['QR Code Display', 'Live Results', 'Full Screen Mode'],
    },
    {
      id: 'participant',
      icon: <Smartphone className="w-16 h-16 text-purple-400" />,
      title: 'Participant Interface',
      description: 'Mobile-optimized interaction and engagement',
      link: '/participant',
      features: ['Quick Join', 'Touch Interactions', 'Real-time Feedback'],
    },
  ]

  const platformFeatures = [
    {
      icon: <Users className="w-12 h-12 text-cyan-400" />,
      title: 'Multi-Persona Design',
      description: 'Tailored interfaces for admins, viewers, and participants with role-specific optimizations.',
    },
    {
      icon: <BarChart3 className="w-12 h-12 text-cyan-400" />,
      title: 'Real-Time Engagement',
      description: 'Live polling, instant feedback, and synchronized activities across all connected devices.',
    },
    {
      icon: <Zap className="w-12 h-12 text-cyan-400" />,
      title: 'Session Management',
      description: 'Complete lifecycle management from session creation to results analysis and reporting.',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      <section className="relative py-20 px-6 text-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-cyan-500/10"></div>
        <div className="relative max-w-6xl mx-auto">
          <div className="flex items-center justify-center gap-6 mb-8">
            <div className="w-20 h-20 md:w-24 md:h-24 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <Users className="w-12 h-12 md:w-14 md:h-14 text-white" />
            </div>
            <h1 className="text-5xl md:text-7xl font-bold text-white">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                CAJA
              </span>
            </h1>
          </div>
          <p className="text-2xl md:text-3xl text-gray-300 mb-4 font-light">
            Interactive Engagement Platform
          </p>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto mb-12">
            Transform your events with real-time polling, interactive activities, and seamless multi-device engagement.
          </p>
        </div>
      </section>

      <section className="py-16 px-6 max-w-7xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-4">
          Choose Your Interface
        </h2>
        <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
          Select the interface that matches your role in the session
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {personas.map((persona) => (
            <Link
              key={persona.id}
              to={persona.link}
              className="group bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-8 hover:border-blue-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10 hover:scale-105"
            >
              <div className="text-center mb-6">
                <div className="flex justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  {persona.icon}
                </div>
                <h3 className="text-2xl font-semibold text-white mb-3 group-hover:text-blue-400 transition-colors">
                  {persona.title}
                </h3>
                <p className="text-gray-400 leading-relaxed mb-6">
                  {persona.description}
                </p>
                <div className="space-y-2">
                  {persona.features.map((feature, index) => (
                    <div key={index} className="text-sm text-gray-500 bg-slate-700/50 rounded-full px-3 py-1 inline-block mr-2">
                      {feature}
                    </div>
                  ))}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="py-16 px-6 max-w-7xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-12">
          Platform Features
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {platformFeatures.map((feature, index) => (
            <div
              key={index}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-cyan-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10"
            >
              <div className="mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-white mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
