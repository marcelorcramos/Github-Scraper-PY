import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";

const Header = () => {
  return (
    <header className="flex justify-end p-4">
      <FontAwesomeIcon icon={faGithub} className="text-white text-[70px]" />
    </header>
  );
};

export default Header;