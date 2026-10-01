import type { ReactNode } from 'react';

type Props = {
  number: string;
  title: string;
  description: string;
  children: ReactNode;
};

export default function InputBlock({ number, title, description, children }: Props) {
  return (
    <div className="input-block">
      <div className="input-title">
        <span className="step-number">{number}</span>
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </div>
      {children}
    </div>
  );
}
