import { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSkills } from '../App';

export default function AllSkillsPage() {
    const data = useSkills();
    const navigate = useNavigate();
    const [query, setQuery] = useState('');

    const allSkills = useMemo(() => {
        if (!data) return [];
        const skills = [];
        for (const cat of data.categories) {
            for (const skill of cat.skills) {
                skills.push({ ...skill, categoryName: cat.name, categorySlug: cat.slug });
            }
            for (const sc of cat.subcategories) {
                for (const skill of sc.skills) {
                    skills.push({
                        ...skill,
                        categoryName: `${cat.name} / ${sc.name}`,
                        categorySlug: cat.slug,
                    });
                }
            }
        }
        return skills.sort((a, b) => a.name.localeCompare(b.name));
    }, [data]);

    const filtered = useMemo(() => {
        if (!query.trim()) return allSkills;
        const q = query.toLowerCase();
        return allSkills.filter(
            s =>
                s.name.toLowerCase().includes(q) ||
                s.description.toLowerCase().includes(q) ||
                (s.id && s.id.toLowerCase().includes(q)) ||
                s.categoryName.toLowerCase().includes(q)
        );
    }, [allSkills, query]);

    if (!data) {
        return (
            <div className="page-container">
                <div style={{ padding: '80px 0', textAlign: 'center' }}>Loading...</div>
            </div>
        );
    }

    return (
        <div className="page-container">
            <div className="breadcrumb">
                <Link to="/">Home</Link>
                <span className="breadcrumb-sep">/</span>
                <span className="breadcrumb-current">All Skills</span>
            </div>

            <div className="all-skills-header animate-in">
                <h1>All Skills</h1>
                <p className="category-header-count">
                    {filtered.length} of {allSkills.length} skills
                </p>
            </div>

            <div className="all-skills-search animate-in animate-in-delay-1">
                <div className="search-wrapper">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Filter skills by name, description, ID, or category..."
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                </div>
            </div>

            <div className="skills-grid animate-in animate-in-delay-2">
                {filtered.map(skill => (
                    <div
                        key={skill.path}
                        className="skill-card"
                        onClick={() => navigate(`/skill/${skill.path}`)}
                    >
                        <div className="skill-card-header">
                            <div className="skill-card-name">{skill.name}</div>
                            {skill.id && <div className="skill-card-id">{skill.id}</div>}
                        </div>
                        <div className="skill-card-desc">{skill.description}</div>
                        <div className="skill-card-footer">
                            <span className="search-result-cat">{skill.categoryName}</span>
                            {skill.commands.slice(0, 3).map(cmd => (
                                <span key={cmd} className="skill-chip command">
                                    {cmd}
                                </span>
                            ))}
                            {skill.commands.length > 3 && (
                                <span className="skill-chip command">+{skill.commands.length - 3}</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {filtered.length === 0 && (
                <div className="empty-state">
                    <div className="empty-state-icon">🔍</div>
                    <h3>No skills match "{query}"</h3>
                    <p>Try a different search term</p>
                </div>
            )}
        </div>
    );
}
