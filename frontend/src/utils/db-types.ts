// frontend/src/utils/db-types.ts

export type Slide = 
  | ShortBulletsSlide 
  | MarkdownSlide 
  | SimpleMermaidSlide 
  | SectionHeaderSlide 
  | PresentationTitleSlide;

export interface BaseSlide {
  user_id: string;
  presentation_id: string;
  slide_id: string;
  topic_id?: string;
  slide_title: string;
  id: string;
  hidden?: boolean;
  previous?: string;
  next?: string;
  generation_messages?: LLMMessage[];
  speaker_notes?: string;
  script?: string;
  [key: string]: any;
}

export interface Excerpt {
  source_id: string;
  excerpt_id: string;
  text: string;
}

export interface Image {
  s3_key?: string;
  url?: string;
  prompt: string;
  negative_prompt?: string;
  style?: string;
  model: string;
  width: number;
  height: number;
  shape: string;
  type: string;
}

export interface IconData {
  name: string;
  source: string;
  detailed_name?: string;
}

export interface ShortBulletsSlide extends BaseSlide {
  slide_type: 'short_bullets_slide';
  slide_content: ShortBulletContent[];
  sequential: boolean;
  layout: 'list' | 'grid';
}

export interface ShortBulletContent {
  content: string;
  source_excerpt_id: string;
  excerpt: Excerpt | null;
  icon: IconData;
  id: string;
}

export interface SimpleMermaidSlide extends BaseSlide {
  slide_type: 'simple_mermaid_slide';
  slide_content: {
    mermaid_code: string;
    excerpts: Excerpt[];
    light_svg: string;
    dark_svg: string;
  };
}

export interface MarkdownSlide extends BaseSlide {
  slide_type: 'markdown_slide';
  slide_content: {
    content: string;
    footnotes: Record<string, Excerpt>;
    prose_class?: string;
  };
}

export interface SectionHeaderSlide extends BaseSlide {
  slide_type: 'section_header_slide';
  slide_title: string;
  image: Image;
  image_position: 'left' | 'right';
}

export interface PresentationTitleSlide extends BaseSlide {
  slide_type: 'presentation_title_slide';
  slide_title: string;
  image: Image;
}

export interface LLMMessage {
  role: string;
  content: string;
}

// New types added

export interface Topic {
  user_id: string;
  presentation_id: string;
  topic_id: string;
  title?: string;
  reduced_docs?: any;
  [key: string]: any;
}

export interface Source {
  user_id: string;
  presentation_id: string;
  source_id: string;
  name?: string;
  char_count?: number;
  s3_filepath?: string;
  summary?: string;
  time_updated?: number;
  type?: string;
  url?: string;
  web_source?: any;
  whole_document_path?: string;
  [key: string]: any;
}

export interface Presentation {
  user_id: string;
  presentation_id: string;
  audience?: string;
  candidate_topics?: any;
  current_slide_id?: string;
  goal?: string;
  head_slide_id?: string;
  interface_data?: any;
  memory?: any;
  messages?: any;
  outline?: any;
  slide_generation_status?: string;
  status?: string;
  time_updated?: number;
  topic?: string;
  topic_extraction_status?: string;
  [key: string]: any;
}
