import { useState, useMemo, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSkills } from '../App';

export default function SearchBar() {
    const data = useSkills();
    const navigate = useNavigate();
    const [query, setQuery] = useState('');
    const [isFocused, setIsFocused] = useState(false);
    const wrapperRef = useRef(null);

    // Flatten all skills for searching
    const allSkills = useMemo(() => {
        if (!data) return [];
        const skills = [];
        for (const cat of data.categories) {
            for (const skill of cat.skills) {
                skills.push({ ...skill, categoryName: cat.name, categoryIcon: cat.icon });
            }
            for (const sc of cat.subcategories) {
                for (const skill of sc.skills) {
                    skills.push({
                        ...skill,
                        categoryName: `${cat.name} / ${sc.name}`,
                        categoryIcon: cat.icon,
                    });
                }
            }
        }
        return skills;
    }, [data]);

    // Search results
    const results = useMemo(() => {
        if (!query.trim()) return [];
        const q = query.toLowerCase();
        return allSkills
            .filter(
                s =>
                    s.name.toLowerCase().includes(q) ||
                    s.description.toLowerCase().includes(q) ||
                    (s.id && s.id.toLowerCase().includes(q))
            )
            .slice(0, 8);
    }, [allSkills, query]);

    // Close on click outside
    useEffect(() => {
        function handleClickOutside(e) {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
                setIsFocused(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    function handleSelect(skill) {
        setQuery('');
        setIsFocused(false);
        navigate(`/skill/${skill.path}`);
    }

    function handleKeyDown(e) {
        if (e.key === 'Escape') {
            setIsFocused(false);
            e.target.blur();
        }
    }

    const showResults = isFocused && query.trim().length > 0;

    return (
        <div className="search-container" ref={wrapperRef}>
            <div className="search-wrapper">
                <span className="search-icon">🔍</span>
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search skills by name, description, or ID..."
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onKeyDown={handleKeyDown}
                />
            </div>

            {showResults && (
                <div className="search-results">
                    {results.length > 0 ? (
                        results.map(skill => (
                            <div
                                key={skill.path}
                                className="search-result-item"
                                onClick={() => handleSelect(skill)}
                            >
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div className="search-result-name">{skill.name}</div>
                                    <div className="search-result-desc">{skill.description}</div>
                                </div>
                                <span className="search-result-cat">{skill.categoryName}</span>
                            </div>
                        ))
                    ) : (
                        <div className="search-no-results">
                            No skills matching "{query}"
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
