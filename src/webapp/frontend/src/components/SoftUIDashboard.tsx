import React from 'react';

interface StatCardProps {
  icon: string;
  number: string | number;
  label: string;
  trend?: string;
  trendType?: 'positive' | 'negative';
}

interface ProjectData {
  name: string;
  logo: string;
  members: string[];
  budget: string;
  completion: number;
}

const StatCard: React.FC<StatCardProps> = ({ icon, number, label, trend, trendType }) => {
  return (
    <div className="stat-card-soft soft-fade-in">
      <div className="stat-icon">
        <i className={icon}></i>
      </div>
      <div className="stat-number">{number}</div>
      <div className="stat-label">{label}</div>
      {trend && (
        <div className={`stat-trend ${trendType}`}>
          {trendType === 'positive' ? '+' : ''}{trend}
        </div>
      )}
    </div>
  );
};

const ProjectRow: React.FC<{ project: ProjectData }> = ({ project }) => {
  return (
    <tr>
      <td>
        <div className="flex items-center gap-3">
          <img 
            src={project.logo} 
            alt={project.name}
            className="w-6 h-6 rounded"
          />
          <span className="font-medium">{project.name}</span>
        </div>
      </td>
      <td>
        <div className="flex -space-x-2">
          {project.members.slice(0, 4).map((member, index) => (
            <div 
              key={index}
              className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 border-2 border-white flex items-center justify-center text-white text-xs font-semibold"
              title={`Team Member ${index + 1}`}
            >
              {index + 1}
            </div>
          ))}
          {project.members.length > 4 && (
            <div className="w-8 h-8 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center text-gray-600 text-xs font-semibold">
              +{project.members.length - 4}
            </div>
          )}
        </div>
      </td>
      <td className="font-semibold">{project.budget}</td>
      <td>
        <div className="flex items-center gap-2">
          <div className="progress-soft flex-1">
            <div 
              className="progress-soft-bar" 
              style={{ width: `${project.completion}%` }}
            ></div>
          </div>
          <span className="text-sm font-semibold text-gray-600">
            {project.completion}%
          </span>
        </div>
      </td>
    </tr>
  );
};

const SoftUIDashboard: React.FC = () => {
  const statsData = [
    {
      icon: 'fas fa-users',
      number: '1,600',
      label: 'Users Active',
      trend: '55%',
      trendType: 'positive' as const
    },
    {
      icon: 'fas fa-mouse-pointer',
      number: '357',
      label: 'Click Events',
      trend: '124%',
      trendType: 'positive' as const
    },
    {
      icon: 'fas fa-shopping-cart',
      number: '2,300',
      label: 'Purchases',
      trend: '15%',
      trendType: 'positive' as const
    },
    {
      icon: 'fas fa-heart',
      number: '940',
      label: 'Likes',
      trend: '90%',
      trendType: 'positive' as const
    }
  ];

  const projectsData: ProjectData[] = [
    {
      name: 'AI Code Reviewer XD Version',
      logo: '🎨',
      members: ['Team1', 'Team2', 'Team3', 'Team4'],
      budget: '$14,000',
      completion: 60
    },
    {
      name: 'Add Progress Tracking',
      logo: '📊',
      members: ['Team1', 'Team2'],
      budget: '$3,000',
      completion: 10
    },
    {
      name: 'Fix Platform Errors',
      logo: '🔧',
      members: ['Team1', 'Team2'],
      budget: 'Not set',
      completion: 100
    },
    {
      name: 'Launch Mobile App',
      logo: '📱',
      members: ['Team1', 'Team2', 'Team3', 'Team4'],
      budget: '$20,500',
      completion: 100
    },
    {
      name: 'Add New Pricing Page',
      logo: '💰',
      members: ['Team1'],
      budget: '$500',
      completion: 25
    },
    {
      name: 'Redesign New Online Shop',
      logo: '🛍️',
      members: ['Team1', 'Team2'],
      budget: '$2,000',
      completion: 40
    }
  ];

  const reviewsData = [
    { type: 'Positive Reviews', percentage: 80, color: 'var(--soft-success)' },
    { type: 'Neutral Reviews', percentage: 17, color: 'var(--soft-warning)' },
    { type: 'Negative Reviews', percentage: 3, color: 'var(--soft-danger)' }
  ];

  const ordersData = [
    { title: '$2400, Design changes', time: '22 DEC 7:20 PM', icon: '💰' },
    { title: 'New order #1832412', time: '21 DEC 11 PM', icon: '📦' },
    { title: 'Server payments for April', time: '21 DEC 9:34 PM', icon: '💳' },
    { title: 'New card added for order #4395133', time: '20 DEC 2:20 AM', icon: '💳' },
    { title: 'Unlock packages for development', time: '18 DEC 4:54 AM', icon: '🔓' },
    { title: 'New order #9583120', time: '17 DEC', icon: '📦' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 soft-gradient-text">
            Dashboard
          </h1>
          <p className="text-gray-600">Welcome to your AI Code Reviewer dashboard</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statsData.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Projects Table */}
          <div className="lg:col-span-2">
            <div className="card-soft">
              <div className="card-soft-header">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-semibold text-gray-900">Projects</h3>
                  <span className="text-sm text-gray-500">30 done this month</span>
                </div>
              </div>
              <div className="card-soft-body">
                <div className="overflow-x-auto">
                  <table className="table-soft">
                    <thead>
                      <tr>
                        <th>Companies</th>
                        <th>Members</th>
                        <th>Budget</th>
                        <th>Completion</th>
                      </tr>
                    </thead>
                    <tbody>
                      {projectsData.map((project, index) => (
                        <ProjectRow key={index} project={project} />
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Reviews Card */}
            <div className="card-soft">
              <div className="card-soft-header">
                <h3 className="text-lg font-semibold text-gray-900">Reviews</h3>
              </div>
              <div className="card-soft-body">
                <div className="space-y-4">
                  {reviewsData.map((review, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{review.type}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full"
                            style={{ 
                              width: `${review.percentage}%`, 
                              backgroundColor: review.color 
                            }}
                          />
                        </div>
                        <span className="text-sm font-semibold text-gray-700">
                          {review.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 pt-4 border-t border-gray-100">
                  <p className="text-sm text-gray-600">
                    More than <strong>1,500,000</strong> developers used our products and over{' '}
                    <strong>700,000</strong> projects were created.
                  </p>
                  <button className="btn-soft btn-soft-primary btn-soft-sm mt-3">
                    View all reviews
                  </button>
                </div>
              </div>
            </div>

            {/* Orders Overview */}
            <div className="card-soft">
              <div className="card-soft-header">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">Orders overview</h3>
                  <span className="badge-soft badge-soft-success">24% this month</span>
                </div>
              </div>
              <div className="card-soft-body">
                <div className="space-y-3">
                  {ordersData.map((order, index) => (
                    <div key={index} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="text-lg">{order.icon}</div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{order.title}</p>
                        <p className="text-xs text-gray-500">{order.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          {/* Built by developers */}
          <div className="card-soft" style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}>
            <div className="card-soft-body">
              <h4 className="text-xl font-bold mb-2">AI Code Reviewer</h4>
              <p className="text-white/90 mb-4">
                From code analysis, security checks to AI suggestions, you will find comprehensive documentation.
              </p>
              <button className="btn-soft btn-soft-sm" style={{ 
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.3)'
              }}>
                Read More
              </button>
            </div>
          </div>

          {/* Work with rockets */}
          <div className="card-soft" style={{ 
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white'
          }}>
            <div className="card-soft-body">
              <h4 className="text-xl font-bold mb-2">Work with AI Power</h4>
              <p className="text-white/90 mb-4">
                Modern development is about leveraging AI. Take the opportunity to enhance your code quality first.
              </p>
              <button className="btn-soft btn-soft-sm" style={{ 
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.3)'
              }}>
                Read More
              </button>
            </div>
          </div>
        </div>

        {/* Active Users Section */}
        <div className="card-soft mt-8">
          <div className="card-soft-header">
            <h3 className="text-lg font-semibold text-gray-900">Active Users</h3>
            <span className="badge-soft badge-soft-success">(+23%) than last week</span>
          </div>
          <div className="card-soft-body">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl mb-2">📄</div>
                <h4 className="text-3xl font-bold text-gray-900">36K</h4>
                <p className="text-sm text-gray-600 uppercase tracking-wide">Users</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">🚀</div>
                <h4 className="text-3xl font-bold text-gray-900">2m</h4>
                <p className="text-sm text-gray-600 uppercase tracking-wide">Clicks</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">💳</div>
                <h4 className="text-3xl font-bold text-gray-900">435$</h4>
                <p className="text-sm text-gray-600 uppercase tracking-wide">Sales</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">⚙️</div>
                <h4 className="text-3xl font-bold text-gray-900">43</h4>
                <p className="text-sm text-gray-600 uppercase tracking-wide">Items</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SoftUIDashboard; 