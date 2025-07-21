import React from 'react';

const Card = ({ 
  children, 
  className = '', 
  padding = true,
  hover = false,
  gradient = false,
  ...props 
}) => {
  const baseClasses = 'card';
  
  const modifierClasses = [
    padding && 'card-padding',
    hover && 'card-hover',
    gradient && 'bg-gradient-to-br from-white to-neutral-50'
  ].filter(Boolean).join(' ');
  
  const classes = `${baseClasses} ${modifierClasses} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

export default Card;