import { useParams, Link, useNavigate } from 'react-router-dom';
import { useSkills } from '../App';

function SkillCard({ skill }) {
    const navigate = useNavigate();
    const maxChips = 4;

    return (
        <div
            className="skill-card"
            onClick={() => navigate(`/skill/${skill.path}`)}
        >
            <div className="skill-card-header">
                <div className="skill-card-name">{skill.name}</div>
                {skill.id && <div className="skill-card-id">{skill.id}</div>}
            </div>
            <div className="skill-card-desc">{skill.description}</div>
            <div className="skill-card-footer">
                {skill.commands.slice(0, maxChips).map(cmd => (
                    <span key={cmd} className="skill-chip command">
                        {cmd}
                    </span>
                ))}
                {skill.commands.length > maxChips && (
                    <span className="skill-chip command">+{skill.commands.length - maxChips}</span>
                )}
                {skill.env && skill.env.length > 0 && (
                    <span className="skill-chip env">🔑 {skill.env.length} env</span>
                )}
            </div>
        </div>
    );
}

export default function CategoryPage() {
    const { slug, subSlug } = useParams();
    const data = useSkills();

    if (!data) {
        return (
            <div className="page-container">
                <div style={{ padding: '80px 0', textAlign: 'center' }}>Loading...</div>
            </div>
        );
    }

    const category = data.categories.find(c => c.slug === slug);

    if (!category) {
        return (
            <div className="page-container">
                <div className="empty-state">
                    <div className="empty-state-icon">🔍</div>
                    <h3>Category not found</h3>
                    <Link to="/" className="back-link">← Back to Home</Link>
                </div>
            </div>
        );
    }

    // If subSlug is provided, show only that subcategory
    if (subSlug) {
        const subcategory = category.subcategories.find(sc => sc.slug === subSlug);
        if (!subcategory) {
            return (
                <div className="page-container">
                    <div className="empty-state">
                        <div className="empty-state-icon">🔍</div>
                        <h3>Subcategory not found</h3>
                        <Link to={`/category/${slug}`} className="back-link">← Back to {category.name}</Link>
                    </div>
                </div>
            );
        }

        return (
            <div className="page-container">
                <div className="breadcrumb">
                    <Link to="/">Home</Link>
                    <span className="breadcrumb-sep">/</span>
                    <Link to={`/category/${slug}`}>{category.name}</Link>
                    <span className="breadcrumb-sep">/</span>
                    <span className="breadcrumb-current">{subcategory.name}</span>
                </div>

                <div className="category-header animate-in">
                    <div className="category-header-icon">{category.icon}</div>
                    <h1>{subcategory.name}</h1>
                    <p className="category-header-count">
                        {subcategory.skills.length} skill{subcategory.skills.length !== 1 ? 's' : ''}
                    </p>
                </div>

                <div className="skills-grid animate-in animate-in-delay-1">
                    {subcategory.skills.map(skill => (
                        <SkillCard key={skill.slug} skill={skill} />
                    ))}
                </div>
            </div>
        );
    }

    const totalSkills =
        category.skills.length +
        category.subcategories.reduce((sum, sc) => sum + sc.skills.length, 0);

    return (
        <div className="page-container">
            <div className="breadcrumb">
                <Link to="/">Home</Link>
                <span className="breadcrumb-sep">/</span>
                <span className="breadcrumb-current">{category.name}</span>
            </div>

            <div className="category-header animate-in">
                <div className="category-header-icon">{category.icon}</div>
                <h1>{category.name}</h1>
                <p className="category-header-count">
                    {totalSkills} skill{totalSkills !== 1 ? 's' : ''}
                    {category.subcategories.length > 0 &&
                        ` across ${category.subcategories.length} subcategories`}
                </p>
            </div>

            {/* Subcategories with links */}
            {category.subcategories.length > 0 && (
                <div className="categories-grid animate-in animate-in-delay-1" style={{ marginBottom: 48 }}>
                    {category.subcategories.map((sc, i) => (
                        <Link
                            to={`/category/${slug}/${sc.slug}`}
                            key={sc.slug}
                            className={`category-card animate-in animate-in-delay-${Math.min(i + 1, 6)}`}
                        >
                            <div className="category-card-name">{sc.name}</div>
                            <div className="category-card-count">
                                {sc.skills.length} skill{sc.skills.length !== 1 ? 's' : ''}
                            </div>
                            <span className="category-card-arrow">→</span>
                        </Link>
                    ))}
                </div>
            )}

            {/* Direct skills (not in subcategories) */}
            {category.skills.length > 0 && (
                <section className="animate-in animate-in-delay-2">
                    {category.subcategories.length > 0 && (
                        <h2 className="subcategory-title">General Skills</h2>
                    )}
                    <div className="skills-grid">
                        {category.skills.map(skill => (
                            <SkillCard key={skill.slug} skill={skill} />
                        ))}
                    </div>
                </section>
            )}

            {/* All subcategory skills inline (when no subcategory drill-down) */}
            {category.subcategories.map(sc => (
                <section key={sc.slug} className="subcategory-section animate-in animate-in-delay-3">
                    <h2 className="subcategory-title">
                        {sc.name}
                        <span style={{ fontWeight: 400, color: 'var(--text-tertiary)', marginLeft: 8, fontSize: '0.85rem' }}>
                            {sc.skills.length}
                        </span>
                    </h2>
                    <div className="skills-grid">
                        {sc.skills.map(skill => (
                            <SkillCard key={skill.slug} skill={skill} />
                        ))}
                    </div>
                </section>
            ))}
        </div>
    );
}
