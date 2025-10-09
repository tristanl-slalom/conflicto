import React from 'react';
import { Clock, Users, CheckCircle, XCircle } from 'lucide-react';

interface SessionStatusIndicatorProps {
  status: 'draft' | 'active' | 'completed';
  participantCount?: number;
  className?: string;
}

const SessionStatusIndicator: React.FC<SessionStatusIndicatorProps> = ({ 
  status, 
  participantCount = 0, 
  className = '' 
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'draft':
        return {
          icon: Clock,
          text: 'Waiting for session to start',
          subText: `${participantCount} participant${participantCount !== 1 ? 's' : ''} waiting`,
          bgColor: 'bg-amber-900/20',
          borderColor: 'border-amber-500/30',
          textColor: 'text-amber-300',
          iconColor: 'text-amber-400'
        };
      case 'active':
        return {
          icon: Users,
          text: 'Session is active',
          subText: `${participantCount} participant${participantCount !== 1 ? 's' : ''} active`,
          bgColor: 'bg-green-900/20',
          borderColor: 'border-green-500/30',
          textColor: 'text-green-300',
          iconColor: 'text-green-400'
        };
      case 'completed':
        return {
          icon: CheckCircle,
          text: 'Session completed',
          subText: 'Thank you for participating',
          bgColor: 'bg-blue-900/20',
          borderColor: 'border-blue-500/30',
          textColor: 'text-blue-300',
          iconColor: 'text-blue-400'
        };
      default:
        return {
          icon: XCircle,
          text: 'Unknown status',
          subText: '',
          bgColor: 'bg-gray-900/20',
          borderColor: 'border-gray-500/30',
          textColor: 'text-gray-300',
          iconColor: 'text-gray-400'
        };
    }
  };

  const config = getStatusConfig();
  const IconComponent = config.icon;

  return (
    <div 
      className={`
        ${config.bgColor} ${config.borderColor} ${config.textColor}
        border rounded-xl p-4 backdrop-blur-sm
        ${className}
      `}
    >
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg bg-slate-800/50 ${config.iconColor}`}>
          <IconComponent className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="font-medium">{config.text}</div>
          {config.subText && (
            <div className="text-sm opacity-75 mt-1">{config.subText}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SessionStatusIndicator;