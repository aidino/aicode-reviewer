FROM node:20-alpine

WORKDIR /app

# Copy package.json và package-lock.json trước
COPY src/webapp/frontend/package*.json ./

# Cài đặt các dependencies với --legacy-peer-deps
RUN npm install --legacy-peer-deps

# Cài đặt thêm các dependencies cho UI components
RUN npm install --legacy-peer-deps axios lucide-react class-variance-authority clsx tailwind-merge sonner \
    @radix-ui/react-dialog @radix-ui/react-select @radix-ui/react-label @radix-ui/react-radio-group \
    @radix-ui/react-slot @radix-ui/react-separator @radix-ui/react-tabs @radix-ui/react-toast

# Copy toàn bộ thư mục frontend
COPY src/webapp/frontend/ .

# Khởi động ứng dụng
CMD ["npm", "run", "dev", "--", "--host"] 