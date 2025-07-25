import Header from '../components/Landing/Header';
import Footer from '../components/Landing/Footer';
import HeroSection from '../components/Landing/HeroSection';
import AdvantagesSection from '../components/Landing/AdvantagesSection';
import CoursesSection from '../components/Landing/CourseSection';
import PlatformSection from '../components/Landing/PlatformSection';
import TeachersSection from '../components/Landing/TeachersSection';
import ReviewsSection from '../components/Landing/ReviewSection';
import FAQSection from '../components/Landing/FAQSection';
import ContactsSection from '../components/Landing/ContactSection';

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