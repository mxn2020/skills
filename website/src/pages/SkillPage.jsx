import { useParams, Link } from 'react-router-dom';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useSkills } from '../App';

function findSkillByPath(data, fullPath) {
    if (!data) return null;

    for (const cat of data.categories) {
        for (const skill of cat.skills) {
            if (skill.path === fullPath) return { skill, category: cat };
        }
        for (const sc of cat.subcategories) {
            for (const skill of sc.skills) {
                if (skill.path === fullPath) return { skill, category: cat, subcategory: sc };
            }
        }
    }
    return null;
}

export default function SkillPage() {
    const params = useParams();
    const fullPath = params['*'];
    const data = useSkills();

    if (!data) {
        return (
            <div className="page-container">
                <div style={{ padding: '80px 0', textAlign: 'center' }}>Loading...</div>
            </div>
        );
    }

    const result = findSkillByPath(data, fullPath);

    if (!result) {
        return (
            <div className="page-container">
                <div className="empty-state">
                    <div className="empty-state-icon">🔍</div>
                    <h3>Skill not found</h3>
                    <p>Could not find a skill at path: {fullPath}</p>
                    <Link to="/" className="back-link">← Back to Home</Link>
                </div>
            </div>
        );
    }

    const { skill, category, subcategory } = result;

    return (
        <div className="page-container">
            {/* Breadcrumb */}
            <div className="breadcrumb">
                <Link to="/">Home</Link>
                <span className="breadcrumb-sep">/</span>
                <Link to={`/category/${category.slug}`}>{category.name}</Link>
                {subcategory && (
                    <>
                        <span className="breadcrumb-sep">/</span>
                        <Link to={`/category/${category.slug}/${subcategory.slug}`}>
                            {subcategory.name}
                        </Link>
                    </>
                )}
                <span className="breadcrumb-sep">/</span>
                <span className="breadcrumb-current">{skill.name}</span>
            </div>

            {/* Detail Header */}
            <div className="skill-detail animate-in">
                <div className="skill-detail-header">
                    <div className="skill-detail-meta">
                        {skill.id && <span className="badge badge-id">{skill.id}</span>}
                        <span className="badge badge-version">v{skill.version}</span>
                    </div>
                    <h1>{skill.name}</h1>
                    <p className="skill-detail-desc">{skill.description}</p>

                    {/* Commands */}
                    {skill.commands.length > 0 && (
                        <div className="skill-detail-chips">
                            {skill.commands.map(cmd => (
                                <span key={cmd} className="chip chip-command">
                                    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                                        <path d="M6 2l6 6-6 6" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
                                    </svg>
                                    {cmd}
                                </span>
                            ))}
                        </div>
                    )}

                    {/* Env vars */}
                    {skill.env && skill.env.length > 0 && (
                        <div className="skill-detail-chips" style={{ marginTop: 8 }}>
                            {skill.env.map(e => (
                                <span key={e} className="chip chip-env">
                                    🔑 {e}
                                </span>
                            ))}
                        </div>
                    )}

                    <a
                        href={`https://github.com/mxn2020/skills/tree/main/${skill.path}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="skill-detail-source"
                    >
                        <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
                        </svg>
                        View Source on GitHub
                    </a>
                </div>

                {/* Markdown Body */}
                <div className="markdown-body animate-in animate-in-delay-2">
                    <Markdown remarkPlugins={[remarkGfm]}>{skill.markdownBody}</Markdown>
                </div>
            </div>
        </div>
    );
}
