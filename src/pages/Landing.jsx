import React from 'react';
import Header from '../components/layout/Header/header';
import Footer from '../components/layout/Footer/Footer';
import HeroSection from '../pages/Landing/HeroSection';
import AdvantagesSection from '../pages/Landing/AdvantagesSection';
import CoursesSection from '../pages/Landing/CourseSection';
import PlatformSection from '../pages/Landing/PlatformSection';
import TeachersSection from '../pages/Landing/TeachersSection';
import ReviewsSection from '../pages/Landing/ReviewSection';
import FAQSection from '../pages/Landing/FAQSection';
import ContactsSection from '../pages/Landing/ContactSection';

const Landing = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <HeroSection />
        <AdvantagesSection />
        <CoursesSection />
        <PlatformSection />
        <TeachersSection />
        <ReviewsSection />
        <FAQSection />
        <ContactsSection />
      </main>
      <Footer />
    </div>
  );
};

export default Landing;