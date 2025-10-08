/**
 * Polling Activity Configuration Types
 */

export interface PollingConfig {
  question: string;
  options: string[];
  allow_multiple_choice?: boolean;
  show_live_results?: boolean;
  anonymous_voting?: boolean;
}

export interface PollingResponse {
  selected_options: string[];
}

export interface PollingResults {
  type: 'poll_results';
  question: string;
  options: string[];
  vote_counts: Record<string, number>;
  percentages: Record<string, number>;
  total_responses: number;
  most_popular: string[];
  allow_multiple_choice: boolean;
  show_live_results: boolean;
  last_updated: string;
}
