import React from 'react';
import { cn } from '../../lib/utils';

interface PersonaLayoutProps {
  persona: 'admin' | 'viewer' | 'participant';
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

const personaStyles = {
  admin: {
    gradient: 'from-blue-500 to-purple-500',
    bg: 'from-slate-900 via-slate-800 to-slate-900',
    accent: 'text-blue-400',
  },
  viewer: {
    gradient: 'from-green-500 to-emerald-500',
    bg: 'from-slate-900 via-slate-800 to-slate-900',
    accent: 'text-green-400',
  },
  participant: {
    gradient: 'from-purple-500 to-pink-500',
    bg: 'from-slate-900 via-purple-900 to-slate-900',
    accent: 'text-purple-400',
  },
};

export function PersonaLayout({
  persona,
  title,
  subtitle,
  children,
  className,
}: PersonaLayoutProps) {
  const styles = personaStyles[persona];

  return (
    <div
      className={cn(
        `min-h-screen bg-gradient-to-br ${styles.bg} text-white`,
        className
      )}
    >
      <div className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 bg-gradient-to-r ${styles.gradient} rounded-lg flex items-center justify-center`}
                >
                  <span className="text-white font-bold text-sm">C</span>
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-white">{title}</h1>
                  {subtitle && (
                    <p className="text-sm text-gray-400">{subtitle}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {children}
    </div>
  );
}

interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function Card({ title, children, className }: CardProps) {
  return (
    <div
      className={cn(
        'bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6',
        className
      )}
    >
      {title && (
        <h2 className="text-lg font-medium text-white mb-4">{title}</h2>
      )}
      {children}
    </div>
  );
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  const baseStyles =
    'font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary:
      'bg-slate-600 hover:bg-slate-500 text-white focus:ring-slate-500',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={cn(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export function Input({ label, className, ...props }: InputProps) {
  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
      )}
      <input
        className={cn(
          'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          className
        )}
        {...props}
      />
    </div>
  );
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  children: React.ReactNode;
}

export function Select({ label, className, children, ...props }: SelectProps) {
  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
      )}
      <select
        className={cn(
          'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          className
        )}
        {...props}
      >
        {children}
      </select>
    </div>
  );
}
